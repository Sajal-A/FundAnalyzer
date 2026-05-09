"""
agents/performance_agent.py
────────────────────────────
Performance Analysis Agent.

Responsibilities:
  - Retrieve fund returns vs benchmark (monthly + summary)
  - Identify top-drag sectors and geographies
  - Flag underperformance streaks against business rules
  - Return a structured output dict with source citations
"""

import time
import json
from strands import Agent
from strands.models import OpenAIModel

from core.config import settings
from core.confidence import compute_confidence, source_tier_score
from core.output_formatter import format_source_citation
from tools.db_tools import (
    get_fund_performance,
    get_performance_summary,
    get_sector_attribution,
    get_top_sector_drags,
    get_geographic_attribution,
    get_fund_metadata,
)

SYSTEM_PROMPT = """
You are the Performance Analysis Agent for a Fund Performance Diagnostic AI System.

Your sole responsibility is to analyze quantitative fund performance data and return
a structured JSON analysis. You have access to database tools — use them to retrieve
the data you need.

ALWAYS follow this process:
1. Call get_fund_metadata to understand the fund and its benchmark
2. Call get_fund_performance to get monthly returns vs benchmark
3. Call get_performance_summary to get aggregated stats for the period
4. Call get_top_sector_drags to identify worst contributing sectors
5. Call get_sector_attribution for the full sector breakdown
6. Call get_geographic_attribution to identify regional drags

ALWAYS respond with ONLY a valid JSON object — no preamble, no markdown, no explanation.
The JSON must follow this exact schema:
{
  "agent": "PerformanceAnalysisAgent",
  "fund_id": "<fund_id>",
  "period": "<period>",
  "performance_summary": {
    "avg_fund_return_pct": <float>,
    "avg_benchmark_return_pct": <float>,
    "avg_delta_pct": <float>,
    "total_delta_pct": <float>,
    "months_in_alert": <int>,
    "trend": "DETERIORATING" | "STABLE" | "IMPROVING"
  },
  "top_drag_sectors": [
    {"sector": "<name>", "avg_weight_pct": <float>, "avg_contribution_pct": <float>, "signal": "<text>"}
  ],
  "top_drag_regions": [
    {"region": "<name>", "avg_contribution_pct": <float>}
  ],
  "underperformance_confirmed": <true|false>,
  "citations": [
    {"source_id": "<id>", "table": "<table>", "field": "<field>", "value": <value>}
  ],
  "confidence_inputs": {
    "data_completeness": <0.0-1.0>,
    "data_freshness": <0.0-1.0>,
    "source_trust_tier": <0.0-1.0>
  },
  "agent_reasoning": "<one paragraph explaining your key findings>"
}
""".strip()


def run_performance_agent(fund_id: str, start_date: str, end_date: str) -> dict:
    """
    Invoke the Performance Analysis Agent and return structured results.
    Measures latency for audit logging.
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
            get_fund_performance,
            get_performance_summary,
            get_sector_attribution,
            get_top_sector_drags,
            get_geographic_attribution,
        ],
    )

    query = (
        f"Analyze the performance of fund {fund_id} "
        f"from {start_date} to {end_date}. "
        f"Use start_date='{start_date}' and end_date='{end_date}' for all tool calls."
    )

    t0 = time.time()
    response = agent(query)
    latency_ms = int((time.time() - t0) * 1000)

    # Extract JSON from agent response
    raw = str(response).strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback minimal structure on parse failure
        result = {
            "agent": "PerformanceAnalysisAgent",
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