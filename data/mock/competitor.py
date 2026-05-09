"""
data/mock/seed_competitor.py
─────────────────────────────
Seeds the competitor_funds table with 5 peer funds
across Q1 2026 (monthly data).
Run: python data/mock/seed_competitor.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.database import execute_many
from data.schema.init_db import init_db

# (date, fund_name, return_pct, strategy, differentiator, expense_ratio, morningstar_rank)
COMPETITOR_ROWS = [
    # Jan 2026
    ("2026-01", "Global Alpha Fund",       0.4,  "Defensive",      "Underweight tech; overweight staples", 0.65, "4-Star"),
    ("2026-01", "Horizon World Equity",    0.2,  "Balanced",        "Diversified; lower EM exposure",       0.72, "4-Star"),
    ("2026-01", "Apex Growth Fund",       -0.3,  "Growth",          "High tech; similar EM overweight",     0.80, "3-Star"),
    ("2026-01", "Meridian Global Eq.",     0.1,  "Value/Defensive", "Energy & financials overweight",       0.58, "3-Star"),
    ("2026-01", "Pinnacle World Fund",     0.3,  "Defensive",       "Quality factor tilt; low beta",        0.61, "5-Star"),
    ("2026-01", "GEF001 (Our Fund)",      -0.8,  "Growth/EM",       "Overweight tech + EM",                 0.75, "2-Star"),

    # Feb 2026
    ("2026-02", "Global Alpha Fund",       0.6,  "Defensive",       "Underweight tech; overweight staples", 0.65, "4-Star"),
    ("2026-02", "Horizon World Equity",    0.3,  "Balanced",        "Diversified; lower EM exposure",       0.72, "4-Star"),
    ("2026-02", "Apex Growth Fund",       -0.1,  "Growth",          "High tech; similar EM overweight",     0.80, "3-Star"),
    ("2026-02", "Meridian Global Eq.",     0.2,  "Value/Defensive", "Energy & financials overweight",       0.58, "3-Star"),
    ("2026-02", "Pinnacle World Fund",     0.5,  "Defensive",       "Quality factor tilt; low beta",        0.61, "5-Star"),
    ("2026-02", "GEF001 (Our Fund)",      -0.5,  "Growth/EM",       "Overweight tech + EM",                 0.75, "2-Star"),

    # Mar 2026
    ("2026-03", "Global Alpha Fund",       1.5,  "Defensive",       "Underweight tech; overweight staples", 0.65, "4-Star"),
    ("2026-03", "Horizon World Equity",    0.8,  "Balanced",        "Diversified; lower EM exposure",       0.72, "4-Star"),
    ("2026-03", "Apex Growth Fund",       -0.2,  "Growth",          "High tech; similar EM overweight",     0.80, "3-Star"),
    ("2026-03", "Meridian Global Eq.",     0.4,  "Value/Defensive", "Energy & financials overweight",       0.58, "3-Star"),
    ("2026-03", "Pinnacle World Fund",     0.9,  "Defensive",       "Quality factor tilt; low beta",        0.61, "5-Star"),
    ("2026-03", "GEF001 (Our Fund)",      -1.2,  "Growth/EM",       "Overweight tech + EM",                 0.75, "2-Star"),
]


def seed():
    init_db()
    execute_many(
        """
        INSERT OR REPLACE INTO competitor_funds
            (date, fund_name, return_pct, strategy,
             differentiator, expense_ratio, morningstar_rank)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        COMPETITOR_ROWS,
    )
    print(f"Seeded {len(COMPETITOR_ROWS)} competitor fund records.")


if __name__ == "__main__":
    seed()