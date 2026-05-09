"""
data/mock/seed_market_intelligence.py
──────────────────────────────────────
Seeds macro_indicators, market_sector_performance,
and risk_events tables.
Run: python data/mock/seed_market_intelligence.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.database import execute_many
from data.schema.init_db import init_db

# (date, indicator, trend, value, notes)
MACRO_ROWS = [
    ("2026-01", "US Federal Funds Rate",  "Rising",  5.75, "Fed signals prolonged higher rates"),
    ("2026-01", "US CPI Inflation",       "Stable",  3.20, "Above target but stabilising"),
    ("2026-01", "US GDP Growth",          "Slowing", 1.80, "Growth decelerating vs Q4 2025"),
    ("2026-01", "China GDP Growth",       "Falling", 4.10, "Slowdown concerns persist"),
    ("2026-01", "EUR/USD Exchange Rate",  "Falling", 1.06, "Dollar strengthening on rate differentials"),

    ("2026-02", "US Federal Funds Rate",  "Rising",  5.75, "No cut expected in H1 2026"),
    ("2026-02", "US CPI Inflation",       "Rising",  3.40, "Slight uptick — hawkish pressure"),
    ("2026-02", "US GDP Growth",          "Slowing", 1.70, "Below consensus estimate"),
    ("2026-02", "China GDP Growth",       "Falling", 3.90, "Property sector drag continuing"),
    ("2026-02", "EUR/USD Exchange Rate",  "Falling", 1.04, "Euro under pressure"),

    ("2026-03", "US Federal Funds Rate",  "Rising",  6.00, "Surprise 25bps hike — risk-off trigger"),
    ("2026-03", "US CPI Inflation",       "Rising",  3.60, "Core CPI above expectations"),
    ("2026-03", "US GDP Growth",          "Slowing", 1.50, "Near stall speed"),
    ("2026-03", "China GDP Growth",       "Falling", 3.70, "Worst reading since 2023"),
    ("2026-03", "EUR/USD Exchange Rate",  "Falling", 1.02, "Near parity — EM currency spillover"),
]

# (date, sector, return_pct, signal)
MARKET_SECTOR_ROWS = [
    ("2026-01", "Technology",       -1.20, "Rate-sensitive sell-off"),
    ("2026-01", "Emerging Markets", -1.50, "Dollar strength + China concerns"),
    ("2026-01", "Financials",       -0.30, "Neutral — rate benefit offset by credit risk"),
    ("2026-01", "Healthcare",        0.60, "Defensive rotation into healthcare"),
    ("2026-01", "Consumer Staples",  0.50, "Defensive — outperforming in risk-off"),
    ("2026-01", "Energy",           -0.20, "Oil price softness"),

    ("2026-02", "Technology",       -1.50, "Earnings misses + rate pressure"),
    ("2026-02", "Emerging Markets", -1.80, "Currency volatility escalating"),
    ("2026-02", "Financials",       -0.40, "Loan quality concerns"),
    ("2026-02", "Healthcare",        0.80, "M&A activity supporting sector"),
    ("2026-02", "Consumer Staples",  0.70, "Safe haven inflows"),
    ("2026-02", "Energy",           -0.10, "Slight recovery on supply cuts"),

    ("2026-03", "Technology",       -2.00, "Broad sell-off — discount rate impact"),
    ("2026-03", "Emerging Markets", -2.20, "Fed hike triggers EM capital outflows"),
    ("2026-03", "Financials",       -0.60, "Credit spread widening"),
    ("2026-03", "Healthcare",        0.90, "Strong defensive positioning"),
    ("2026-03", "Consumer Staples",  0.80, "Highest inflows in 18 months"),
    ("2026-03", "Energy",           -0.30, "Demand slowdown concerns"),
]

# (date, event, severity)
RISK_EVENT_ROWS = [
    ("2026-01", "US Fed signals prolonged higher interest rates",           "HIGH"),
    ("2026-01", "China Q4 2025 GDP below consensus at 4.1%",               "MEDIUM"),
    ("2026-01", "Global equity markets enter elevated volatility regime",   "MEDIUM"),
    ("2026-02", "US CPI uptick surprises markets — rate cut hopes fade",   "HIGH"),
    ("2026-02", "China property sector defaults accelerate",                "HIGH"),
    ("2026-02", "Institutional investors reduce growth portfolio exposure", "MEDIUM"),
    ("2026-02", "Geopolitical tensions in Eastern Europe escalate",         "MEDIUM"),
    ("2026-03", "Fed surprise 25bps hike — risk-off triggered globally",   "HIGH"),
    ("2026-03", "EM currency basket hits 3-year low vs USD",               "HIGH"),
    ("2026-03", "Tech sector enters correction territory (>10% drawdown)", "HIGH"),
    ("2026-03", "Emerging market capital outflow accelerates post-hike",   "HIGH"),
]


def seed():
    init_db()
    execute_many(
        """
        INSERT OR REPLACE INTO macro_indicators
            (date, indicator, trend, value, notes)
        VALUES (?, ?, ?, ?, ?)
        """,
        MACRO_ROWS,
    )
    execute_many(
        """
        INSERT OR REPLACE INTO market_sector_performance
            (date, sector, return_pct, signal)
        VALUES (?, ?, ?, ?)
        """,
        MARKET_SECTOR_ROWS,
    )
    execute_many(
        """
        INSERT INTO risk_events (date, event, severity)
        VALUES (?, ?, ?)
        """,
        RISK_EVENT_ROWS,
    )
    print(
        f"Seeded {len(MACRO_ROWS)} macro rows, "
        f"{len(MARKET_SECTOR_ROWS)} market sector rows, "
        f"{len(RISK_EVENT_ROWS)} risk event rows."
    )


if __name__ == "__main__":
    seed()