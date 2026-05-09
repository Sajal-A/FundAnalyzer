"""
core/output_formatter.py
────────────────────────
Formats the orchestrator's synthesized findings into a
clean, structured executive response dict.
Also builds the "Show Your Work" audit view.
"""

from datetime import datetime, timezone


def format_executive_response(
    trace_id: str,
    fund_id: str,
    period: str,
    overall_confidence: str,
    confidence_score: float,
    total_latency_ms: int,
    root_cause: dict,
    peer_comparison: dict,
    recommendations: list[dict],
    conflicts: list[dict],
) -> dict:
    """
    Build the standard executive response object.
    This is what the advisor sees by default.
    """
    return {
        "trace_id":           trace_id,
        "fund_id":            fund_id,
        "period":             period,
        "generated_at":       datetime.now(timezone.utc).isoformat(),
        "latency_ms":         total_latency_ms,
        "overall_confidence": {
            "level": overall_confidence,
            "score": confidence_score,
        },
        "root_cause":         root_cause,
        "peer_comparison":    peer_comparison,
        "recommendations":    recommendations,
        "conflicts_detected": len(conflicts) > 0,
        "conflicts_summary":  _summarise_conflicts(conflicts),
        "disclaimer": (
            "This analysis is AI-generated from mock data for POC purposes. "
            "All findings include source citations. Use ?mode=detailed for full audit trail."
        ),
    }


def format_detailed_response(
    executive_response: dict,
    agent_calls: list[dict],
    conflicts: list[dict],
    query_parsed: dict,
    dispatch_plan: list[dict],
) -> dict:
    """
    Build the Show Your Work response — full audit chain.
    Activated via ?mode=detailed.
    """
    return {
        **executive_response,
        "show_your_work": {
            "query_parsing":   query_parsed,
            "dispatch_plan":   dispatch_plan,
            "agent_calls":     _format_agent_calls(agent_calls),
            "conflicts_detail": _format_conflicts(conflicts),
            "note": "This view exposes all intermediate reasoning steps, raw data, and tool calls.",
        },
    }


def _summarise_conflicts(conflicts: list[dict]) -> list[dict]:
    return [
        {
            "conflict_id":   c.get("conflict_id"),
            "topic":         c.get("topic"),
            "resolution":    c.get("resolution"),
            "winning_agent": c.get("winning_agent"),
        }
        for c in conflicts
    ]


def _format_agent_calls(agent_calls: list[dict]) -> list[dict]:
    return [
        {
            "agent":       c.get("agent_name"),
            "latency_ms":  c.get("latency_ms"),
            "confidence":  c.get("confidence"),
            "called_at":   c.get("called_at"),
            "output":      c.get("output_payload"),
        }
        for c in agent_calls
    ]


def _format_conflicts(conflicts: list[dict]) -> list[dict]:
    return [
        {
            "conflict_id":   c.get("conflict_id"),
            "agent_a":       c.get("agent_a"),
            "agent_b":       c.get("agent_b"),
            "topic":         c.get("topic"),
            "resolution":    c.get("resolution"),
            "winning_agent": c.get("winning_agent"),
            "detected_at":   c.get("detected_at"),
        }
        for c in conflicts
    ]


def format_source_citation(
    source_id: str,
    source_type: str,
    table_name: str,
    field: str,
    value,
    date_range: str,
    agent: str,
    verified: bool = True,
) -> dict:
    """Build a standard source citation object attached to every finding."""
    return {
        "source_id":    source_id,
        "source_type":  source_type,
        "table_name":   table_name,
        "field":        field,
        "value":        value,
        "date_range":   date_range,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "agent":        agent,
        "verified":     verified,
    }