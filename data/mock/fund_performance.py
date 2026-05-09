"""
data/mock/seed_fund_performance.py
───────────────────────────────────
Seeds fund_metadata and fund_performance tables.
Run: python data/mock/seed_fund_performance.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.database import execute, execute_many
from data.schema.init_db import init_db

FUND_METADATA = (
    "GEF001",
    "Global Equity Fund",
    "MSCI World Index",
    "Global Large Cap Equity",
    "USD",
    "fund_return < benchmark_return - 50bps for 2+ consecutive months",
    5.0,
)

# (fund_id, date, fund_return_pct, benchmark_return_pct, performance_delta_pct, alert_flag)
PERFORMANCE_ROWS = [
    ("GEF001", "2025-10",  0.8,  0.6,  0.2,  None),
    ("GEF001", "2025-11",  0.3,  0.5, -0.2,  None),
    ("GEF001", "2025-12",  0.1,  0.4, -0.3,  None),
    ("GEF001", "2026-01", -0.8,  0.5, -1.3,  "ALERT"),
    ("GEF001", "2026-02", -0.5,  0.3, -0.8,  "ALERT"),
    ("GEF001", "2026-03", -1.2,  0.4, -1.6,  "ALERT"),
]


def seed():
    init_db()
    execute(
        """
        INSERT OR REPLACE INTO fund_metadata
            (fund_id, fund_name, benchmark, category, base_currency,
             underperformance_rule, outflow_alert_threshold_pct)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        FUND_METADATA,
    )
    execute_many(
        """
        INSERT OR REPLACE INTO fund_performance
            (fund_id, date, fund_return_pct, benchmark_return_pct,
             performance_delta_pct, alert_flag)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        PERFORMANCE_ROWS,
    )
    print(f"Seeded {len(PERFORMANCE_ROWS)} fund performance records.")


if __name__ == "__main__":
    seed()