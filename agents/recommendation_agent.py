"""
agents/recommendation_agent.py
────────────────────────────────
Recommendation Agent.

Responsibilities:
  - Synthesize outputs from all four Group A agents
  - Generate 3-5 prioritized, actionable recommendations
  - Validate each recommendation against fund mandate
  - Assign checkpoint tiers (GREEN / AMBER / RED)
  - Return structured output
"""

import time
import json
from strands import Agent
from strands.models import OpenAIModel

from core.config import settings
from tools.db_tools import get_fund_metadata
from tools.vector_tools import search_analyst_commentary

SYSTEM_PROMPT = """
You are the Recommendation Agent for a Fund Performance Diagnostic AI System.

You receive synthesized findings from four specialist agents:
  - PerformanceAnalysisAgent: quantitative fund performance data
  - FundFlowAgent:            AUM and distribution flow data
  - MarketIntelligenceAgent:  macro and sector market context
  - CompetitorIntelligenceAgent: peer benchmarking data

Your job is to generate 3-5 prioritized, actionable recommendations across three domains:
  1. PORTFOLIO   — sector/allocation changes
  2. DISTRIBUTION — client engagement and channel actions
  3. POSITIONING  — fund narrative and marketing
  4. RISK         — hedging and risk management

IMPORTANT RULES:
- Every recommendation must have a clear rationale referencing specific agent findings
- Recommendations must not violate fund mandate (provided in context)
- Each recommendation must have a PRIORITY: HIGH | MEDIUM | LOW
- Each recommendation must have a CHECKPOINT_TIER: GREEN | AMBER | RED
  (RED = requires analyst sign-off, AMBER = advisor review, GREEN = auto-cleared)
- Portfolio changes >10% weight shift automatically get checkpoint tier RED

ALWAYS respond with ONLY a valid JSON object — no preamble, no markdown, no explanation.
The JSON must follow this exact schema:
{
  "agent": "RecommendationAgent",
  "fund_id": "<fund_id>",
  "period": "<period>",
  "recommendations": [
    {
      "id": "REC-001",
      "domain": "PORTFOLIO" | "DISTRIBUTION" | "POSITIONING" | "RISK",
      "action": "<clear, actionable instruction>",
      "rationale": "<2-3 sentences citing specific agent findings>",
      "priority": "HIGH" | "MEDIUM" | "LOW",
      "expected_impact": "<measurable expected outcome>",
      "checkpoint_tier": "GREEN" | "AMBER" | "RED",
      "supporting_agents": ["<AgentName1>", "<AgentName2>"]
    }
  ],
  "mandate_validation": {
    "checks_performed": <int>,
    "violations_found": <int>,
    "violations": []
  },
  "synthesis_summary": "<2-3 paragraph executive narrative combining all findings into a coherent story>",
  "confidence_inputs": {
    "data_completeness": <0.0-1.0>,
    "inter_agent_consistency": <0.0-1.0>,
    "source_trust_tier": <0.0-1.0>
  },
  "agent_reasoning": "<one paragraph on how you synthesized the agent outputs>"
}
""".strip()


def run_recommendation_agent(
    fund_id: str,
    start_date: str,
    end_date: str,
    performance_result: dict,
    flow_result: dict,
    market_result: dict,
    competitor_result: dict,
) -> dict:
    """
    Invoke the Recommendation Agent with all Group A agent outputs.
    Runs sequentially after the parallel group completes.
    """
    model = OpenAIModel(
        model_id=settings.openai_model,
        params={
            "temperature": settings.openai_temperature,
            "max_tokens":  settings.openai_max_tokens,
        },
    )

    agent = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[
            get_fund_metadata,
            search_analyst_commentary,
        ],
    )

    # Build rich context from all agent outputs
    context = f"""
Fund ID: {fund_id}
Analysis Period: {start_date} to {end_date}

=== PERFORMANCE ANALYSIS AGENT FINDINGS ===
{json.dumps(performance_result, indent=2)}

=== FUND FLOW AGENT FINDINGS ===
{json.dumps(flow_result, indent=2)}

=== MARKET INTELLIGENCE AGENT FINDINGS ===
{json.dumps(market_result, indent=2)}

=== COMPETITOR INTELLIGENCE AGENT FINDINGS ===
{json.dumps(competitor_result, indent=2)}

=== INSTRUCTIONS ===
Based on the above findings from all four specialist agents:
1. Call get_fund_metadata('{fund_id}') to understand fund mandate constraints
2. Call search_analyst_commentary with a query about recommendations for this fund
3. Generate 3-5 prioritized recommendations
4. Validate each against fund mandate before including
5. Return the structured JSON response
""".strip()

    t0 = time.time()
    response = agent(context)
    latency_ms = int((time.time() - t0) * 1000)

    raw = str(response).strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {
            "agent": "RecommendationAgent",
            "fund_id": fund_id,
            "period": f"{start_date} to {end_date}",
            "error": "Failed to parse agent JSON response",
            "raw_response": raw[:500],
            "recommendations": [],
            "confidence_inputs": {
                "data_completeness":       0.3,
                "inter_agent_consistency": 0.5,
                "source_trust_tier":       1.0,
            },
        }

    result["latency_ms"] = latency_ms
    return result