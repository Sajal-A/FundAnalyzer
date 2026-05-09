"""
agents/market_agent.py
───────────────────────
Market Intelligence Agent.

Responsibilities:
  - Retrieve macroeconomic indicators for the period
  - Retrieve market-wide sector performance
  - Identify key risk events
  - Use RAG (ChromaDB) to find corroborating analyst commentary and news
  - Return structured output with source citations including vector store results
"""

import time
import json
from strands import Agent
from strands.models import OpenAIModel

from core.config import settings
from tools.db_tools import (
    get_macro_indicators,
    get_market_sector_performance,
    get_risk_events,
)
from tools.vector_tools import (
    search_analyst_commentary,
    search_news_sentiment,
)

SYSTEM_PROMPT = """
You are the Market Intelligence Agent for a Fund Performance Diagnostic AI System.

Your sole responsibility is to provide macroeconomic and market context that explains
the external environment during the analysis period. You combine structured data with
unstructured analyst commentary and news via semantic search.

ALWAYS follow this process:
1. Call get_macro_indicators to get interest rates, inflation, GDP trends
2. Call get_market_sector_performance to get market-wide sector returns
3. Call get_risk_events with severity='HIGH' to identify major risk events
4. Call search_analyst_commentary with a query about macro factors and sector trends
5. Call search_news_sentiment to find relevant news context

ALWAYS respond with ONLY a valid JSON object — no preamble, no markdown, no explanation.
The JSON must follow this exact schema:
{
  "agent": "MarketIntelligenceAgent",
  "period": "<period>",
  "macro_environment": {
    "overall_signal": "RISK_OFF" | "NEUTRAL" | "RISK_ON",
    "key_headwinds": ["<headwind1>", "<headwind2>"],
    "key_tailwinds": ["<tailwind1>"],
    "primary_macro_driver": "<single most impactful macro factor>"
  },
  "sector_context": [
    {"sector": "<name>", "market_return_pct": <float>, "signal": "<text>"}
  ],
  "high_severity_risk_events": [
    {"date": "<date>", "event": "<text>", "severity": "HIGH"}
  ],
  "analyst_insights": [
    {"document_id": "<id>", "summary": "<2-sentence summary>", "similarity": <float>}
  ],
  "news_context": [
    {"document_id": "<id>", "summary": "<2-sentence summary>", "similarity": <float>}
  ],
  "correlation_to_fund_performance": "<paragraph explaining how macro environment
    specifically impacted the fund's portfolio given its known tech + EM overweight>",
  "citations": [
    {"source_id": "<id>", "source_type": "structured_db|vector_store", "table_or_doc": "<name>"}
  ],
  "confidence_inputs": {
    "data_completeness": <0.0-1.0>,
    "data_freshness": <0.0-1.0>,
    "source_trust_tier": <0.0-1.0>,
    "vector_similarity": <0.0-1.0>
  },
  "agent_reasoning": "<one paragraph summarising the macro picture and its fund impact>"
}
""".strip()


def run_market_agent(start_date: str, end_date: str) -> dict:
    """
    Invoke the Market Intelligence Agent and return structured results.
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
            get_macro_indicators,
            get_market_sector_performance,
            get_risk_events,
            search_analyst_commentary,
            search_news_sentiment,
        ],
    )

    query = (
        f"Analyze the macroeconomic environment and market conditions "
        f"from {start_date} to {end_date}. "
        f"Focus on factors impacting technology and emerging market equities. "
        f"Use start_date='{start_date}' and end_date='{end_date}' for all DB tool calls."
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
            "agent": "MarketIntelligenceAgent",
            "period": f"{start_date} to {end_date}",
            "error": "Failed to parse agent JSON response",
            "raw_response": raw[:500],
            "confidence_inputs": {
                "data_completeness": 0.3,
                "data_freshness":    1.0,
                "source_trust_tier": 0.8,
                "vector_similarity": 0.5,
            },
        }

    result["latency_ms"] = latency_ms
    return result