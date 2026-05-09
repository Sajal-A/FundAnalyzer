"""
agents/orchestrator.py
───────────────────────
Orchestrator Agent — the central coordinator.

Workflow:
  1. Parse and validate the incoming query
  2. Dispatch Group A agents IN PARALLEL (asyncio.gather)
       - PerformanceAnalysisAgent
       - FundFlowAgent
       - MarketIntelligenceAgent
       - CompetitorIntelligenceAgent
  3. Detect and resolve inter-agent conflicts
  4. Invoke RecommendationAgent SEQUENTIALLY with all Group A results
  5. Compute overall confidence score
  6. Format executive response
  7. Write full audit trail
"""

import asyncio
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from loguru import logger

from agents.performance_agent  import run_performance_agent
from agents.flow_agent          import run_flow_agent
from agents.market_agent        import run_market_agent
from agents.competitor_agent    import run_competitor_agent
from agents.recommendation_agent import run_recommendation_agent

from core.audit import (
    generate_trace_id,
    log_session_start,
    log_agent_result,
    log_conflict,
    log_session_complete,
    log_session_error,
    get_agent_calls,
    get_conflicts,
)
from core.confidence import compute_confidence, checkpoint_tier
from core.output_formatter import (
    format_executive_response,
    format_detailed_response,
)
from core.exceptions import OrchestratorError

# ── Agent priority for conflict resolution (lower index = higher priority) ────
AGENT_PRIORITY = [
    "PerformanceAnalysisAgent",
    "MarketIntelligenceAgent",
    "FundFlowAgent",
    "CompetitorIntelligenceAgent",
    "RecommendationAgent",
]


def _parse_period(period: str) -> tuple[str, str]:
    """
    Convert a period string (e.g. '2026-Q1') into start/end YYYY-MM dates.
    Supports:
        '2026-Q1' → ('2026-01', '2026-03')
        '2026-Q2' → ('2026-04', '2026-06')
        '2026-Q3' → ('2026-07', '2026-09')
        '2026-Q4' → ('2026-10', '2026-12')
    Also accepts explicit 'YYYY-MM:YYYY-MM' format.
    """
    p = period.strip().upper()
    if ":" in p:
        parts = p.split(":")
        return parts[0].lower(), parts[1].lower()

    if "Q" in p:
        year, q = p.split("-Q")
        quarter_map = {"1": ("01","03"), "2": ("04","06"), "3": ("07","09"), "4": ("10","12")}
        start_m, end_m = quarter_map.get(q, ("01","03"))
        return f"{year}-{start_m}", f"{year}-{end_m}"

    # Default: treat as single month
    return p.lower(), p.lower()


def _detect_conflicts(
    performance: dict,
    market: dict,
    trace_id: str,
) -> list[dict]:
    """
    Compare Performance Agent and Market Agent signals for consistency.
    Returns list of conflict dicts (may be empty).
    """
    conflicts = []

    # Check: macro signal vs fund performance signal
    perf_trend  = performance.get("performance_summary", {}).get("trend", "")
    macro_signal = market.get("macro_environment", {}).get("overall_signal", "")

    # If performance is deteriorating but macro is RISK_ON, flag conflict
    if perf_trend == "DETERIORATING" and macro_signal == "RISK_ON":
        conflict_id = f"CON-{trace_id}-001"
        conflict = {
            "conflict_id":   conflict_id,
            "agent_a":       "PerformanceAnalysisAgent",
            "agent_b":       "MarketIntelligenceAgent",
            "topic":         "Fund performance trend vs macro environment signal",
            "resolution":    "PerformanceAnalysisAgent given priority (domain priority rule: internal quantitative data outranks external signal)",
            "winning_agent": "PerformanceAnalysisAgent",
        }
        conflicts.append(conflict)
        log_conflict(trace_id=trace_id, **conflict)
        logger.warning(f"Conflict detected: {conflict_id}")

    return conflicts


def _compute_overall_confidence(
    performance: dict,
    flow: dict,
    market: dict,
    competitor: dict,
    conflicts: list[dict],
) -> tuple[str, float]:
    """Aggregate confidence scores from all Group A agents."""

    def _ci(agent_result: dict) -> dict:
        return agent_result.get("confidence_inputs", {})

    # Average data completeness across agents
    completeness_scores = [
        _ci(performance).get("data_completeness",  1.0),
        _ci(flow).get("data_completeness",         1.0),
        _ci(market).get("data_completeness",       1.0),
        _ci(competitor).get("data_completeness",   1.0),
    ]
    avg_completeness = sum(completeness_scores) / len(completeness_scores)

    # Inter-agent consistency: reduce by 0.15 per conflict
    consistency = max(0.0, 1.0 - (len(conflicts) * 0.15))

    # Average freshness
    freshness_scores = [
        _ci(performance).get("data_freshness",  1.0),
        _ci(flow).get("data_freshness",         1.0),
        _ci(market).get("data_freshness",       1.0),
        _ci(competitor).get("data_freshness",   1.0),
    ]
    avg_freshness = sum(freshness_scores) / len(freshness_scores)

    # Average source trust tier
    trust_scores = [
        _ci(performance).get("source_trust_tier",  1.0),
        _ci(flow).get("source_trust_tier",         1.0),
        _ci(market).get("source_trust_tier",       0.8),   # external data
        _ci(competitor).get("source_trust_tier",   0.8),
    ]
    avg_trust = sum(trust_scores) / len(trust_scores)

    # Vector similarity from market agent (only agent using RAG)
    vector_sim = _ci(market).get("vector_similarity", 1.0)

    result = compute_confidence(
        data_completeness       = avg_completeness,
        inter_agent_consistency = consistency,
        data_freshness          = avg_freshness,
        source_trust_tier       = avg_trust,
        vector_similarity       = vector_sim,
    )
    return result.level, result.score


async def _run_group_a_parallel(
    fund_id: str,
    start_date: str,
    end_date: str,
    trace_id: str,
) -> tuple[dict, dict, dict, dict]:
    """
    Run the four Group A agents in parallel using a thread pool
    (Strands agents are synchronous — we parallelise via threads).
    """
    loop = asyncio.get_event_loop()

    with ThreadPoolExecutor(max_workers=4) as executor:
        perf_future = loop.run_in_executor(
            executor, run_performance_agent, fund_id, start_date, end_date
        )
        flow_future = loop.run_in_executor(
            executor, run_flow_agent, fund_id, start_date, end_date
        )
        market_future = loop.run_in_executor(
            executor, run_market_agent, start_date, end_date
        )
        competitor_future = loop.run_in_executor(
            executor, run_competitor_agent, fund_id, start_date, end_date
        )

        performance, flow, market, competitor = await asyncio.gather(
            perf_future, flow_future, market_future, competitor_future
        )

    # Log each agent result to audit trail
    for agent_result, name in [
        (performance, "PerformanceAnalysisAgent"),
        (flow,        "FundFlowAgent"),
        (market,      "MarketIntelligenceAgent"),
        (competitor,  "CompetitorIntelligenceAgent"),
    ]:
        ci = agent_result.get("confidence_inputs", {})
        conf_level = "HIGH" if ci.get("data_completeness", 1) > 0.8 else "MEDIUM"
        log_agent_result(
            trace_id       = trace_id,
            agent_name     = name,
            input_payload  = {"fund_id": fund_id, "start_date": start_date, "end_date": end_date},
            output_payload = agent_result,
            latency_ms     = agent_result.get("latency_ms", 0),
            confidence     = conf_level,
        )
        logger.info(f"{name} completed in {agent_result.get('latency_ms', 0)}ms")

    return performance, flow, market, competitor


def run_orchestrator(
    query: str,
    fund_id: str,
    period: str,
    user_id: str = "system",
    detailed: bool = False,
) -> dict:
    """
    Main entry point — called by the API layer.

    Args:
        query:    Raw natural language query from the user
        fund_id:  Fund identifier (e.g. 'GEF001')
        period:   Period string (e.g. '2026-Q1')
        user_id:  Identifier of the requesting user
        detailed: If True, include Show Your Work audit chain in response

    Returns:
        Formatted response dict (executive or detailed view)
    """
    total_start = time.time()
    trace_id    = generate_trace_id()
    start_date, end_date = _parse_period(period)

    query_parsed = {
        "fund_id":    fund_id,
        "period":     period,
        "start_date": start_date,
        "end_date":   end_date,
        "intent":     "underperformance_diagnosis",
    }

    dispatch_plan = [
        {"group": "A", "mode": "parallel",   "agent": "PerformanceAnalysisAgent"},
        {"group": "A", "mode": "parallel",   "agent": "FundFlowAgent"},
        {"group": "A", "mode": "parallel",   "agent": "MarketIntelligenceAgent"},
        {"group": "A", "mode": "parallel",   "agent": "CompetitorIntelligenceAgent"},
        {"group": "B", "mode": "sequential", "agent": "RecommendationAgent",
         "depends_on": "Group A completion"},
    ]

    logger.info(f"[{trace_id}] Orchestrator started — fund={fund_id}, period={period}")
    log_session_start(trace_id, user_id, query, query_parsed)

    try:
        # ── Step 1: Run Group A in parallel ───────────────────────────────────
        logger.info(f"[{trace_id}] Dispatching Group A agents in parallel...")
        performance, flow, market, competitor = asyncio.run(
            _run_group_a_parallel(fund_id, start_date, end_date, trace_id)
        )

        # ── Step 2: Detect conflicts ──────────────────────────────────────────
        logger.info(f"[{trace_id}] Checking for inter-agent conflicts...")
        conflicts = _detect_conflicts(performance, market, trace_id)
        logger.info(f"[{trace_id}] Conflicts detected: {len(conflicts)}")

        # ── Step 3: Run Recommendation Agent sequentially ─────────────────────
        logger.info(f"[{trace_id}] Invoking RecommendationAgent (sequential)...")
        recommendation = run_recommendation_agent(
            fund_id         = fund_id,
            start_date      = start_date,
            end_date        = end_date,
            performance_result  = performance,
            flow_result         = flow,
            market_result       = market,
            competitor_result   = competitor,
        )
        log_agent_result(
            trace_id       = trace_id,
            agent_name     = "RecommendationAgent",
            input_payload  = {"fund_id": fund_id, "period": period},
            output_payload = recommendation,
            latency_ms     = recommendation.get("latency_ms", 0),
            confidence     = "HIGH",
        )
        logger.info(f"RecommendationAgent completed in {recommendation.get('latency_ms', 0)}ms")

        # ── Step 4: Compute overall confidence ────────────────────────────────
        overall_confidence, confidence_score = _compute_overall_confidence(
            performance, flow, market, competitor, conflicts
        )

        # ── Step 5: Determine checkpoint tier ────────────────────────────────
        recs = recommendation.get("recommendations", [])
        has_high_impact = any(
            "10%" in r.get("action", "") or "rebalance" in r.get("action", "").lower()
            for r in recs
        )
        ckpt = checkpoint_tier(
            confidence_level  = overall_confidence,
            is_recommendation = True,
            impact_pct        = 11.0 if has_high_impact else 5.0,
        )

        # ── Step 6: Format response ───────────────────────────────────────────
        total_latency_ms = int((time.time() - total_start) * 1000)

        root_cause = {
            "performance_summary":    performance.get("performance_summary", {}),
            "top_drag_sectors":       performance.get("top_drag_sectors", []),
            "top_drag_regions":       performance.get("top_drag_regions", []),
            "macro_environment":      market.get("macro_environment", {}),
            "high_severity_events":   market.get("high_severity_risk_events", []),
            "correlation_to_performance": market.get("correlation_to_fund_performance", ""),
        }

        peer_comparison = {
            "category_benchmark":    competitor.get("category_benchmark", {}),
            "top_performing_peers":  competitor.get("top_performing_peers", []),
            "strategy_gap_analysis": competitor.get("strategy_gap_analysis", ""),
        }

        exec_response = format_executive_response(
            trace_id           = trace_id,
            fund_id            = fund_id,
            period             = period,
            overall_confidence = overall_confidence,
            confidence_score   = confidence_score,
            total_latency_ms   = total_latency_ms,
            root_cause         = root_cause,
            peer_comparison    = peer_comparison,
            recommendations    = recs,
            conflicts          = conflicts,
        )

        # ── Step 7: Write completed audit record ──────────────────────────────
        log_session_complete(
            trace_id           = trace_id,
            overall_confidence = overall_confidence,
            confidence_score   = confidence_score,
            checkpoint_tier    = ckpt,
            output_snapshot    = exec_response,
            total_latency_ms   = total_latency_ms,
        )

        logger.success(
            f"[{trace_id}] Orchestration complete — "
            f"confidence={overall_confidence}({confidence_score}), "
            f"tier={ckpt}, latency={total_latency_ms}ms"
        )

        # Return detailed or standard view
        if detailed:
            agent_calls = get_agent_calls(trace_id)
            conflict_records = get_conflicts(trace_id)
            return format_detailed_response(
                executive_response = exec_response,
                agent_calls        = agent_calls,
                conflicts          = conflict_records,
                query_parsed       = query_parsed,
                dispatch_plan      = dispatch_plan,
            )

        return exec_response

    except Exception as e:
        log_session_error(trace_id, str(e))
        logger.error(f"[{trace_id}] Orchestration failed: {e}")
        raise OrchestratorError(f"Orchestration failed for trace {trace_id}: {e}") from e