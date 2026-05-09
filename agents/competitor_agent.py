"""
agents/competitor_agent.py
───────────────────────────
Competitor Intelligence Agent.

Responsibilities:
  - Benchmark fund against category peers
  - Calculate category average return and gap in bps
  - Identify strategies of outperforming peers
  - Flag positioning differentiation opportunities
"""

import time
import json
from strands import Agent
from strands.models import OpenAIModel

from core.config import settings
from tools.db_tools import (
    get_peer_performance,
    get_category_summary,
    get_fund_metadata,
)

SYSTEM_PROMPT = """
You are the Competitor Intelligence Agent for a Fund Performance Diagnostic AI System.

Your sole responsibility is to benchmark the fund's performance against category peers
and identify strategic insights from peer positioning. You have access to competitor
fund data.

ALWAYS follow this process:
1. Call get_fund_metadata to understand the fund being analyzed
2. Call get_peer_performance to get all peer fund returns for the period
3. Call get_category_summary to get the category average, best/worst peer, and our gap

ALWAYS respond with ONLY a valid JSON object — no preamble, no markdown, no explanation.
The JSON must follow this exact schema:
{
  "agent": "CompetitorIntelligenceAgent",
  "period": "<period>",
  "category_benchmark": {
    "category_avg_return_pct": <float>,
    "our_fund_avg_return_pct": <float>,
    "gap_vs_category_bps": <float>,
    "our_fund_rank": "<e.g. 6th of 6 peers>",
    "relative_position": "BOTTOM_QUARTILE" | "THIRD_QUARTILE" | "SECOND_QUARTILE" | "TOP_QUARTILE"
  },
  "top_performing_peers": [
    {
      "fund_name": "<name>",
      "avg_return_pct": <float>,
      "strategy": "<strategy>",
      "key_differentiator": "<why they outperformed>"
    }
  ],
  "strategy_gap_analysis": "<paragraph: what do outperforming peers do differently that our fund doesn't>",
  "expense_comparison": {
    "our_expense_ratio": <float>,
    "peer_avg_expense_ratio": <float>,
    "expense_disadvantage": <true|false>
  },
  "positioning_opportunities": [
    "<specific opportunity identified from peer analysis>"
  ],
  "citations": [
    {"source_id": "competitor_funds-<date>-<fund>", "table": "competitor_funds", "field": "return_pct", "value": <value>}
  ],
  "confidence_inputs": {
    "data_completeness": <0.0-1.0>,
    "data_freshness": <0.0-1.0>,
    "source_trust_tier": <0.0-1.0>
  },
  "agent_reasoning": "<one paragraph on peer positioning insights>"
}
""".strip()


def run_competitor_agent(fund_id: str, start_date: str, end_date: str) -> dict:
    """
    Invoke the Competitor Intelligence Agent and return structured results.
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
            get_peer_performance,
            get_category_summary,
        ],
    )

    query = (
        f"Benchmark fund {fund_id} against its category peers "
        f"for the period {start_date} to {end_date}. "
        f"Use start_date='{start_date}' and end_date='{end_date}' for all tool calls."
    )

    t0 = time.time()
    response = agent(query)
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
            "agent": "CompetitorIntelligenceAgent",
            "fund_id": fund_id,
            "period": f"{start_date} to {end_date}",
            "error": "Failed to parse agent JSON response",
            "raw_response": raw[:500],
            "confidence_inputs": {
                "data_completeness": 0.3,
                "data_freshness":    1.0,
                "source_trust_tier": 0.8,
            },
        }

    result["latency_ms"] = latency_ms
    return result