"""
data/schema/init_db.py
──────────────────────
Creates all SQLite tables.
Run once before seeding: python data/schema/init_db.py
Safe to re-run — uses CREATE TABLE IF NOT EXISTS.
"""

import sys
from pathlib import Path

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.database import get_connection
from loguru import logger


SCHEMA_SQL = """

-- ─── Fund Metadata ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fund_metadata (
    fund_id                     TEXT PRIMARY KEY,
    fund_name                   TEXT NOT NULL,
    benchmark                   TEXT NOT NULL,
    category                    TEXT NOT NULL,
    base_currency               TEXT NOT NULL DEFAULT 'USD',
    underperformance_rule       TEXT,
    outflow_alert_threshold_pct REAL DEFAULT 5.0,
    created_at                  TEXT DEFAULT (datetime('now'))
);

-- ─── Fund Performance ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fund_performance (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_id                 TEXT NOT NULL REFERENCES fund_metadata(fund_id),
    date                    TEXT NOT NULL,           -- YYYY-MM
    fund_return_pct         REAL NOT NULL,
    benchmark_return_pct    REAL NOT NULL,
    performance_delta_pct   REAL NOT NULL,           -- fund - benchmark
    alert_flag              TEXT,                    -- NULL | 'WATCH' | 'ALERT' | 'CRITICAL'
    UNIQUE(fund_id, date)
);

-- ─── Sector Attribution ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sector_attribution (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_id             TEXT NOT NULL REFERENCES fund_metadata(fund_id),
    date                TEXT NOT NULL,           -- YYYY-MM
    sector              TEXT NOT NULL,
    weight_pct          REAL NOT NULL,           -- Portfolio weight
    contribution_pct    REAL NOT NULL,           -- Return contribution
    signal              TEXT,                    -- e.g. 'Overweight / Sell-off'
    UNIQUE(fund_id, date, sector)
);

-- ─── Geographic Attribution ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS geographic_attribution (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_id             TEXT NOT NULL REFERENCES fund_metadata(fund_id),
    date                TEXT NOT NULL,           -- YYYY-MM
    region              TEXT NOT NULL,
    weight_pct          REAL NOT NULL,
    contribution_pct    REAL NOT NULL,
    UNIQUE(fund_id, date, region)
);

-- ─── AUM & Fund Flows ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS aum_flows (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_id                 TEXT NOT NULL REFERENCES fund_metadata(fund_id),
    date                    TEXT NOT NULL,       -- YYYY-MM
    aum_usd_mn              REAL NOT NULL,
    net_flow_usd_mn         REAL NOT NULL,
    market_impact_usd_mn    REAL NOT NULL,
    alert_flag              TEXT,
    UNIQUE(fund_id, date)
);

-- ─── Regional Flows ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS regional_flows (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_id         TEXT NOT NULL REFERENCES fund_metadata(fund_id),
    date            TEXT NOT NULL,       -- YYYY-MM
    region          TEXT NOT NULL,
    flow_usd_mn     REAL NOT NULL,
    UNIQUE(fund_id, date, region)
);

-- ─── Channel Flows ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS channel_flows (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_id         TEXT NOT NULL REFERENCES fund_metadata(fund_id),
    date            TEXT NOT NULL,       -- YYYY-MM
    channel         TEXT NOT NULL,       -- Institutional | Advisor | Retail
    flow_usd_mn     REAL NOT NULL,
    UNIQUE(fund_id, date, channel)
);

-- ─── Macro Indicators ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS macro_indicators (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    date        TEXT NOT NULL,       -- YYYY-MM
    indicator   TEXT NOT NULL,
    trend       TEXT NOT NULL,       -- Rising | Falling | Stable
    value       REAL,
    notes       TEXT,
    UNIQUE(date, indicator)
);

-- ─── Sector Performance (Market) ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS market_sector_performance (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date            TEXT NOT NULL,
    sector          TEXT NOT NULL,
    return_pct      REAL NOT NULL,
    signal          TEXT,
    UNIQUE(date, sector)
);

-- ─── Risk Events ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS risk_events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    date        TEXT NOT NULL,
    event       TEXT NOT NULL,
    severity    TEXT NOT NULL        -- LOW | MEDIUM | HIGH
);

-- ─── Competitor / Peer Funds ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS competitor_funds (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date            TEXT NOT NULL,   -- YYYY-MM (for the period)
    fund_name       TEXT NOT NULL,
    return_pct      REAL NOT NULL,
    strategy        TEXT NOT NULL,
    differentiator  TEXT,
    expense_ratio   REAL,
    morningstar_rank TEXT,
    UNIQUE(date, fund_name)
);

-- ─── Audit Log (main session record) ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS audit_log (
    trace_id            TEXT PRIMARY KEY,
    user_id             TEXT NOT NULL DEFAULT 'system',
    query_raw           TEXT NOT NULL,
    query_parsed        TEXT,            -- JSON
    status              TEXT NOT NULL,   -- IN_PROGRESS | COMPLETED | FAILED
    overall_confidence  TEXT,
    confidence_score    REAL,
    checkpoint_tier     TEXT,            -- GREEN | AMBER | RED
    output_snapshot     TEXT,            -- JSON of full response
    total_latency_ms    INTEGER,
    approved_by         TEXT,
    approved_at         TEXT,
    error_message       TEXT,
    created_at          TEXT NOT NULL,
    completed_at        TEXT
);

-- ─── Audit Agent Calls ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS audit_agent_calls (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    trace_id        TEXT NOT NULL REFERENCES audit_log(trace_id),
    agent_name      TEXT NOT NULL,
    input_payload   TEXT,            -- JSON
    output_payload  TEXT,            -- JSON
    latency_ms      INTEGER,
    confidence      TEXT,
    called_at       TEXT NOT NULL
);

-- ─── Audit Conflicts ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS audit_conflicts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    trace_id        TEXT NOT NULL REFERENCES audit_log(trace_id),
    conflict_id     TEXT NOT NULL,
    agent_a         TEXT NOT NULL,
    agent_b         TEXT NOT NULL,
    topic           TEXT NOT NULL,
    resolution      TEXT NOT NULL,
    winning_agent   TEXT NOT NULL,
    detected_at     TEXT NOT NULL
);

-- ─── Indexes ──────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_fund_perf_fund_date    ON fund_performance(fund_id, date);
CREATE INDEX IF NOT EXISTS idx_sector_attr_fund_date  ON sector_attribution(fund_id, date);
CREATE INDEX IF NOT EXISTS idx_aum_flows_fund_date    ON aum_flows(fund_id, date);
CREATE INDEX IF NOT EXISTS idx_audit_log_status       ON audit_log(status);
CREATE INDEX IF NOT EXISTS idx_audit_calls_trace      ON audit_agent_calls(trace_id);
"""


def init_db() -> None:
    logger.info("Initializing SQLite database...")
    with get_connection() as conn:
        conn.executescript(SCHEMA_SQL)
    logger.success("All tables created successfully.")


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    init_db()
    print("Database initialized.")