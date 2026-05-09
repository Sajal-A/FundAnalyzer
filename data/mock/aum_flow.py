"""
data/mock/seed_aum_flows.py
────────────────────────────
Seeds aum_flows, regional_flows, and channel_flows tables.
Run: python data/mock/seed_aum_flows.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.database import execute_many
from data.schema.init_db import init_db

# (fund_id, date, aum_usd_mn, net_flow_usd_mn, market_impact_usd_mn, alert_flag)
AUM_ROWS = [
    ("GEF001", "2025-10", 11200.0,  150.0,  80.0,  None),
    ("GEF001", "2025-11", 11100.0,   50.0, -80.0,  None),
    ("GEF001", "2025-12", 10800.0, -100.0, -50.0,  "WATCH"),
    ("GEF001", "2026-01", 10200.0, -300.0,  200.0, "WATCH"),
    ("GEF001", "2026-02",  9850.0, -420.0, -130.0, "ALERT"),
    ("GEF001", "2026-03",  9100.0, -580.0, -170.0, "CRITICAL"),
]

# (fund_id, date, region, flow_usd_mn)
REGIONAL_ROWS = [
    ("GEF001", "2026-01", "EMEA",          -200.0),
    ("GEF001", "2026-01", "Americas",        -60.0),
    ("GEF001", "2026-01", "APAC",            -40.0),

    ("GEF001", "2026-02", "EMEA",          -250.0),
    ("GEF001", "2026-02", "Americas",        -90.0),
    ("GEF001", "2026-02", "APAC",            -80.0),

    ("GEF001", "2026-03", "EMEA",          -250.0),
    ("GEF001", "2026-03", "Americas",       -130.0),
    ("GEF001", "2026-03", "APAC",           -200.0),
]

# (fund_id, date, channel, flow_usd_mn)
CHANNEL_ROWS = [
    ("GEF001", "2026-01", "Institutional",  -250.0),
    ("GEF001", "2026-01", "Advisor",         -90.0),
    ("GEF001", "2026-01", "Retail",           40.0),

    ("GEF001", "2026-02", "Institutional",  -300.0),
    ("GEF001", "2026-02", "Advisor",        -150.0),
    ("GEF001", "2026-02", "Retail",           30.0),

    ("GEF001", "2026-03", "Institutional",  -250.0),
    ("GEF001", "2026-03", "Advisor",        -110.0),
    ("GEF001", "2026-03", "Retail",           80.0),  # slight retail inflow
]


def seed():
    init_db()
    execute_many(
        """
        INSERT OR REPLACE INTO aum_flows
            (fund_id, date, aum_usd_mn, net_flow_usd_mn,
             market_impact_usd_mn, alert_flag)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        AUM_ROWS,
    )
    execute_many(
        """
        INSERT OR REPLACE INTO regional_flows
            (fund_id, date, region, flow_usd_mn)
        VALUES (?, ?, ?, ?)
        """,
        REGIONAL_ROWS,
    )
    execute_many(
        """
        INSERT OR REPLACE INTO channel_flows
            (fund_id, date, channel, flow_usd_mn)
        VALUES (?, ?, ?, ?)
        """,
        CHANNEL_ROWS,
    )
    print(
        f"Seeded {len(AUM_ROWS)} AUM rows, "
        f"{len(REGIONAL_ROWS)} regional flow rows, "
        f"{len(CHANNEL_ROWS)} channel flow rows."
    )


if __name__ == "__main__":
    seed()