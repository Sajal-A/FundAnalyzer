"""
data/mock/seed_sector_attribution.py
──────────────────────────────────────
Seeds sector_attribution and geographic_attribution tables.
Run: python data/mock/seed_sector_attribution.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.database import execute_many
from data.schema.init_db import init_db

# (fund_id, date, sector, weight_pct, contribution_pct, signal)
SECTOR_ROWS = [
    # Jan 2026
    ("GEF001","2026-01","Technology",       28.5, -0.35, "Overweight / Rate sensitivity"),
    ("GEF001","2026-01","Emerging Markets", 22.0, -0.28, "Currency volatility"),
    ("GEF001","2026-01","Financials",       15.0, -0.08, "Neutral"),
    ("GEF001","2026-01","Healthcare",       12.0,  0.06, "Defensive — positive"),
    ("GEF001","2026-01","Consumer Staples", 10.0,  0.05, "Defensive — positive"),
    ("GEF001","2026-01","Energy",            7.5, -0.06, "Neutral"),
    ("GEF001","2026-01","Other",             5.0,  0.01, "Immaterial"),
    # Feb 2026
    ("GEF001","2026-02","Technology",       28.5, -0.30, "Overweight / Sell-off continues"),
    ("GEF001","2026-02","Emerging Markets", 22.0, -0.25, "China growth concerns"),
    ("GEF001","2026-02","Financials",       15.0, -0.05, "Neutral"),
    ("GEF001","2026-02","Healthcare",       12.0,  0.07, "Defensive — positive"),
    ("GEF001","2026-02","Consumer Staples", 10.0,  0.06, "Defensive — positive"),
    ("GEF001","2026-02","Energy",            7.5, -0.04, "Neutral"),
    ("GEF001","2026-02","Other",             5.0,  0.01, "Immaterial"),
    # Mar 2026
    ("GEF001","2026-03","Technology",       28.5, -0.45, "Overweight / Broad sell-off"),
    ("GEF001","2026-03","Emerging Markets", 22.0, -0.38, "Currency volatility peak"),
    ("GEF001","2026-03","Financials",       15.0, -0.12, "Neutral"),
    ("GEF001","2026-03","Healthcare",       12.0,  0.08, "Defensive — positive"),
    ("GEF001","2026-03","Consumer Staples", 10.0,  0.06, "Defensive — positive"),
    ("GEF001","2026-03","Energy",            7.5, -0.09, "Neutral"),
    ("GEF001","2026-03","Other",             5.0, -0.02, "Immaterial"),
]

# (fund_id, date, region, weight_pct, contribution_pct)
GEO_ROWS = [
    ("GEF001","2026-01","North America",  38.0, -0.20),
    ("GEF001","2026-01","Emerging Markets",22.0,-0.28),
    ("GEF001","2026-01","Europe",         20.0, -0.15),
    ("GEF001","2026-01","Asia Pacific",   15.0, -0.10),
    ("GEF001","2026-01","Other",           5.0, -0.05),

    ("GEF001","2026-02","North America",  38.0, -0.18),
    ("GEF001","2026-02","Emerging Markets",22.0,-0.25),
    ("GEF001","2026-02","Europe",         20.0, -0.12),
    ("GEF001","2026-02","Asia Pacific",   15.0, -0.08),
    ("GEF001","2026-02","Other",           5.0,  0.03),

    ("GEF001","2026-03","North America",  38.0, -0.30),
    ("GEF001","2026-03","Emerging Markets",22.0,-0.38),
    ("GEF001","2026-03","Europe",         20.0, -0.25),
    ("GEF001","2026-03","Asia Pacific",   15.0, -0.18),
    ("GEF001","2026-03","Other",           5.0,  0.01),
]


def seed():
    init_db()
    execute_many(
        """
        INSERT OR REPLACE INTO sector_attribution
            (fund_id, date, sector, weight_pct, contribution_pct, signal)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        SECTOR_ROWS,
    )
    execute_many(
        """
        INSERT OR REPLACE INTO geographic_attribution
            (fund_id, date, region, weight_pct, contribution_pct)
        VALUES (?, ?, ?, ?, ?)
        """,
        GEO_ROWS,
    )
    print(f"Seeded {len(SECTOR_ROWS)} sector rows and {len(GEO_ROWS)} geographic rows.")


if __name__ == "__main__":
    seed()