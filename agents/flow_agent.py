"""
agents/flow_agent.py
─────────────────────
Fund Flow & Distribution Agent.

Responsibilities:
  - Analyze AUM trends and net flow patterns
  - Identify outflow hotspots by region and channel
  - Flag breaches of the 5% AUM outflow alert threshold
  - Return structured output with source citations
"""

import time
import json
from strands import Agent
from strands.models import OpenAIModel

from core.config import settings
from tools.db_tools import (
    get_aum_trends,
    get_flow_summary,
    get_regional_flows,
    get_channel_flows,
    get_fund_metadata,
)

SYSTEM_PROMPT = """
You are the Fund Flow & Distribution Agent for a Fund Performance Diagnostic AI System.

Your sole responsibility is to analyze fund flow data — AUM trends, net inflows/outflows,
and distribution channel breakdown — and return a structured JSON analysis.

ALWAYS follow this process:
1. Call get_fund_metadata to get the outflow alert threshold for the fund
2. Call get_aum_trends to get monthly AUM and net flow data
3. Call get_flow_summary to get aggregated flow stats for the period
4. Call get_regional_flows to see which regions are the largest outflow sources
5. Call get_channel_flows to see which channels (Institutional/Advisor/Retail) are most affected

ALWAYS respond with ONLY a valid JSON object — no preamble, no markdown, no explanation.
The JSON must follow this exact schema:
{
  "agent": "FundFlowAgent",
  "fund_id": "<fund_id>",
  "period": "<period>",
  "aum_summary": {
    "opening_aum_usd_mn": <float>,
    "closing_aum_usd_mn": <float>,
    "aum_change_usd_mn": <float>,
    "aum_change_pct": <float>,
    "total_net_flow_usd_mn": <float>,
    "flow_trend": "ACCELERATING_OUTFLOW" | "STABLE_OUTFLOW" | "IMPROVING" | "INFLOW"
  },
  "alert_breached": <true|false>,
  "top_outflow_regions": [
    {"region": "<name>", "total_flow_usd_mn": <float>}
  ],
  "top_outflow_channels": [
    {"channel": "<name>", "total_flow_usd_mn": <float>}
  ],
  "primary_concern": "<one sentence describing the most urgent flow issue>",
  "citations": [
    {"source_id": "<table>-<fund_id>-<date>", "table": "<table>", "field": "<field>", "value": <value>}
  ],
  "confidence_inputs": {
    "data_completeness": <0.0-1.0>,
    "data_freshness": <0.0-1.0>,
    "source_trust_tier": <0.0-1.0>
  },
  "agent_reasoning": "<one paragraph explaining key flow findings>"
}
""".strip()


def run_flow_agent(fund_id: str, start_date: str, end_date: str) -> dict:
    """
    Invoke the Fund Flow & Distribution Agent and return structured results.
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
            get_aum_trends,
            get_flow_summary,
            get_regional_flows,
            get_channel_flows,
        ],
    )

    query = (
        f"Analyze fund flows and distribution for fund {fund_id} "
        f"from {start_date} to {end_date}. "
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
            "agent": "FundFlowAgent",
            "fund_id": fund_id,
            "period": f"{start_date} to {end_date}",
            "error": "Failed to parse agent JSON response",
            "raw_response": raw[:500],
            "confidence_inputs": {
                "data_completeness": 0.3,
                "data_freshness":    1.0,
                "source_trust_tier": 1.0,
            },
        }

    result["latency_ms"] = latency_ms
    return result