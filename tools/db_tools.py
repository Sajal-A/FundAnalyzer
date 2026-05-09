"""
tools/db_tools.py
──────────────────
All SQLite-backed Strands @tool functions.
These are the atomic data-retrieval functions
called by the specialist sub-agents.
"""

from strands import tool
from core.database import query_all, query_one


# ─── Fund Metadata ────────────────────────────────────────────────────────────

@tool
def get_fund_metadata(fund_id: str) -> dict:
    """
    Retrieve fund metadata including benchmark, category,
    base currency, and business rule definitions.

    Args:
        fund_id: The fund identifier (e.g. 'GEF001')

    Returns:
        Fund metadata dict or empty dict if not found.
    """
    row = query_one(
        "SELECT * FROM fund_metadata WHERE fund_id = ?",
        (fund_id,)
    )
    return row or {}


# ─── Fund Performance ─────────────────────────────────────────────────────────

@tool
def get_fund_performance(fund_id: str, start_date: str, end_date: str) -> list[dict]:
    """
    Retrieve monthly fund performance vs benchmark for a date range.

    Args:
        fund_id:    Fund identifier (e.g. 'GEF001')
        start_date: Start month inclusive in YYYY-MM format (e.g. '2026-01')
        end_date:   End month inclusive in YYYY-MM format   (e.g. '2026-03')

    Returns:
        List of monthly performance records with fund_return_pct,
        benchmark_return_pct, performance_delta_pct, alert_flag.
    """
    return query_all(
        """
        SELECT date, fund_return_pct, benchmark_return_pct,
               performance_delta_pct, alert_flag
        FROM fund_performance
        WHERE fund_id = ?
          AND date >= ? AND date <= ?
        ORDER BY date
        """,
        (fund_id, start_date, end_date),
    )


@tool
def get_performance_summary(fund_id: str, start_date: str, end_date: str) -> dict:
    """
    Get aggregated performance summary for a period:
    average returns, total delta, alert count.

    Args:
        fund_id:    Fund identifier
        start_date: Start month YYYY-MM
        end_date:   End month YYYY-MM

    Returns:
        Summary dict with avg_fund_return, avg_benchmark_return,
        avg_delta, total_delta, alert_months, months_count.
    """
    row = query_one(
        """
        SELECT
            COUNT(*)                        AS months_count,
            ROUND(AVG(fund_return_pct), 4)  AS avg_fund_return,
            ROUND(AVG(benchmark_return_pct),4) AS avg_benchmark_return,
            ROUND(AVG(performance_delta_pct),4) AS avg_delta,
            ROUND(SUM(performance_delta_pct),4) AS total_delta,
            SUM(CASE WHEN alert_flag IS NOT NULL THEN 1 ELSE 0 END) AS alert_months
        FROM fund_performance
        WHERE fund_id = ?
          AND date >= ? AND date <= ?
        """,
        (fund_id, start_date, end_date),
    )
    return row or {}


# ─── Sector Attribution ───────────────────────────────────────────────────────

@tool
def get_sector_attribution(fund_id: str, start_date: str, end_date: str) -> list[dict]:
    """
    Retrieve sector attribution data showing which sectors
    contributed positively or negatively to performance.

    Args:
        fund_id:    Fund identifier
        start_date: Start month YYYY-MM
        end_date:   End month YYYY-MM

    Returns:
        List of sector attribution records with weight_pct,
        contribution_pct, and signal.
    """
    return query_all(
        """
        SELECT date, sector, weight_pct, contribution_pct, signal
        FROM sector_attribution
        WHERE fund_id = ?
          AND date >= ? AND date <= ?
        ORDER BY date, contribution_pct ASC
        """,
        (fund_id, start_date, end_date),
    )


@tool
def get_top_sector_drags(fund_id: str, start_date: str, end_date: str, limit: int = 3) -> list[dict]:
    """
    Retrieve the worst-performing sectors (biggest negative contributors)
    averaged across the period.

    Args:
        fund_id:    Fund identifier
        start_date: Start month YYYY-MM
        end_date:   End month YYYY-MM
        limit:      Number of top drags to return (default 3)

    Returns:
        List of sectors ordered by average contribution ascending.
    """
    return query_all(
        """
        SELECT
            sector,
            ROUND(AVG(weight_pct), 2)       AS avg_weight_pct,
            ROUND(AVG(contribution_pct), 4)  AS avg_contribution_pct,
            ROUND(SUM(contribution_pct), 4)  AS total_contribution_pct
        FROM sector_attribution
        WHERE fund_id = ?
          AND date >= ? AND date <= ?
        GROUP BY sector
        ORDER BY avg_contribution_pct ASC
        LIMIT ?
        """,
        (fund_id, start_date, end_date, limit),
    )


# ─── Geographic Attribution ───────────────────────────────────────────────────

@tool
def get_geographic_attribution(fund_id: str, start_date: str, end_date: str) -> list[dict]:
    """
    Retrieve geographic attribution showing regional performance contributions.

    Args:
        fund_id:    Fund identifier
        start_date: Start month YYYY-MM
        end_date:   End month YYYY-MM

    Returns:
        List of geographic attribution records with region,
        weight_pct, contribution_pct.
    """
    return query_all(
        """
        SELECT date, region, weight_pct, contribution_pct
        FROM geographic_attribution
        WHERE fund_id = ?
          AND date >= ? AND date <= ?
        ORDER BY date, contribution_pct ASC
        """,
        (fund_id, start_date, end_date),
    )


# ─── AUM & Fund Flows ─────────────────────────────────────────────────────────

@tool
def get_aum_trends(fund_id: str, start_date: str, end_date: str) -> list[dict]:
    """
    Retrieve monthly AUM and net flow data for a fund.

    Args:
        fund_id:    Fund identifier
        start_date: Start month YYYY-MM
        end_date:   End month YYYY-MM

    Returns:
        List of monthly AUM records with aum_usd_mn,
        net_flow_usd_mn, market_impact_usd_mn, alert_flag.
    """
    return query_all(
        """
        SELECT date, aum_usd_mn, net_flow_usd_mn,
               market_impact_usd_mn, alert_flag
        FROM aum_flows
        WHERE fund_id = ?
          AND date >= ? AND date <= ?
        ORDER BY date
        """,
        (fund_id, start_date, end_date),
    )


@tool
def get_flow_summary(fund_id: str, start_date: str, end_date: str) -> dict:
    """
    Get aggregated flow summary: total net flows, AUM change,
    and number of alert months.

    Args:
        fund_id:    Fund identifier
        start_date: Start month YYYY-MM
        end_date:   End month YYYY-MM

    Returns:
        Summary dict with total_net_flow, opening_aum,
        closing_aum, aum_change_pct, critical_months.
    """
    rows = query_all(
        """
        SELECT date, aum_usd_mn, net_flow_usd_mn, alert_flag
        FROM aum_flows
        WHERE fund_id = ?
          AND date >= ? AND date <= ?
        ORDER BY date
        """,
        (fund_id, start_date, end_date),
    )
    if not rows:
        return {}

    total_net_flow  = sum(r["net_flow_usd_mn"] for r in rows)
    opening_aum     = rows[0]["aum_usd_mn"]
    closing_aum     = rows[-1]["aum_usd_mn"]
    aum_change      = closing_aum - opening_aum
    aum_change_pct  = round((aum_change / opening_aum) * 100, 2)
    critical_months = sum(1 for r in rows if r["alert_flag"] in ("ALERT", "CRITICAL"))

    return {
        "total_net_flow_usd_mn": round(total_net_flow, 1),
        "opening_aum_usd_mn":    opening_aum,
        "closing_aum_usd_mn":    closing_aum,
        "aum_change_usd_mn":     round(aum_change, 1),
        "aum_change_pct":        aum_change_pct,
        "critical_months":       critical_months,
        "months_count":          len(rows),
    }


@tool
def get_regional_flows(fund_id: str, start_date: str, end_date: str) -> list[dict]:
    """
    Retrieve aggregated net flows by region across a period.

    Args:
        fund_id:    Fund identifier
        start_date: Start month YYYY-MM
        end_date:   End month YYYY-MM

    Returns:
        List of regions with total_flow_usd_mn, ordered worst first.
    """
    return query_all(
        """
        SELECT
            region,
            ROUND(SUM(flow_usd_mn), 1) AS total_flow_usd_mn
        FROM regional_flows
        WHERE fund_id = ?
          AND date >= ? AND date <= ?
        GROUP BY region
        ORDER BY total_flow_usd_mn ASC
        """,
        (fund_id, start_date, end_date),
    )


@tool
def get_channel_flows(fund_id: str, start_date: str, end_date: str) -> list[dict]:
    """
    Retrieve aggregated net flows by distribution channel across a period.

    Args:
        fund_id:    Fund identifier
        start_date: Start month YYYY-MM
        end_date:   End month YYYY-MM

    Returns:
        List of channels with total_flow_usd_mn, ordered worst first.
    """
    return query_all(
        """
        SELECT
            channel,
            ROUND(SUM(flow_usd_mn), 1) AS total_flow_usd_mn
        FROM channel_flows
        WHERE fund_id = ?
          AND date >= ? AND date <= ?
        GROUP BY channel
        ORDER BY total_flow_usd_mn ASC
        """,
        (fund_id, start_date, end_date),
    )


# ─── Market Intelligence ──────────────────────────────────────────────────────

@tool
def get_macro_indicators(start_date: str, end_date: str) -> list[dict]:
    """
    Retrieve macroeconomic indicators for a period.

    Args:
        start_date: Start month YYYY-MM
        end_date:   End month YYYY-MM

    Returns:
        List of macro indicator records with indicator,
        trend, value, and notes.
    """
    return query_all(
        """
        SELECT date, indicator, trend, value, notes
        FROM macro_indicators
        WHERE date >= ? AND date <= ?
        ORDER BY date, indicator
        """,
        (start_date, end_date),
    )


@tool
def get_market_sector_performance(start_date: str, end_date: str) -> list[dict]:
    """
    Retrieve market-wide sector performance returns for a period.
    Used to compare against fund's sector attribution.

    Args:
        start_date: Start month YYYY-MM
        end_date:   End month YYYY-MM

    Returns:
        List of sector market returns ordered by return ascending.
    """
    return query_all(
        """
        SELECT date, sector, return_pct, signal
        FROM market_sector_performance
        WHERE date >= ? AND date <= ?
        ORDER BY date, return_pct ASC
        """,
        (start_date, end_date),
    )


@tool
def get_risk_events(start_date: str, end_date: str, severity: str = None) -> list[dict]:
    """
    Retrieve key risk events for a period, optionally filtered by severity.

    Args:
        start_date: Start month YYYY-MM (matched on YYYY-MM prefix)
        end_date:   End month YYYY-MM
        severity:   Optional filter: 'LOW' | 'MEDIUM' | 'HIGH'

    Returns:
        List of risk events ordered by date and severity.
    """
    if severity:
        return query_all(
            """
            SELECT date, event, severity
            FROM risk_events
            WHERE date >= ? AND date <= ? AND severity = ?
            ORDER BY date, severity DESC
            """,
            (start_date, end_date, severity),
        )
    return query_all(
        """
        SELECT date, event, severity
        FROM risk_events
        WHERE date >= ? AND date <= ?
        ORDER BY date, severity DESC
        """,
        (start_date, end_date),
    )


# ─── Competitor Intelligence ──────────────────────────────────────────────────

@tool
def get_peer_performance(start_date: str, end_date: str) -> list[dict]:
    """
    Retrieve peer fund performance across a period.

    Args:
        start_date: Start month YYYY-MM
        end_date:   End month YYYY-MM

    Returns:
        List of peer fund records with return_pct, strategy,
        differentiator, expense_ratio, morningstar_rank.
    """
    return query_all(
        """
        SELECT date, fund_name, return_pct, strategy,
               differentiator, expense_ratio, morningstar_rank
        FROM competitor_funds
        WHERE date >= ? AND date <= ?
        ORDER BY date, return_pct DESC
        """,
        (start_date, end_date),
    )


@tool
def get_category_summary(start_date: str, end_date: str) -> dict:
    """
    Get category-level peer performance summary:
    average return, best/worst peer, and our fund's relative rank.

    Args:
        start_date: Start month YYYY-MM
        end_date:   End month YYYY-MM

    Returns:
        Summary dict with category_avg_return, best_peer,
        worst_peer, our_fund_return, gap_vs_category_bps.
    """
    rows = query_all(
        """
        SELECT
            fund_name,
            ROUND(AVG(return_pct), 4) AS avg_return
        FROM competitor_funds
        WHERE date >= ? AND date <= ?
        GROUP BY fund_name
        ORDER BY avg_return DESC
        """,
        (start_date, end_date),
    )
    if not rows:
        return {}

    peers      = [r for r in rows if r["fund_name"] != "GEF001 (Our Fund)"]
    our_fund   = next((r for r in rows if r["fund_name"] == "GEF001 (Our Fund)"), None)
    cat_avg    = round(sum(p["avg_return"] for p in peers) / len(peers), 4) if peers else 0

    our_return = our_fund["avg_return"] if our_fund else None
    gap_bps    = round((our_return - cat_avg) * 100, 1) if our_return is not None else None

    return {
        "category_avg_return_pct": cat_avg,
        "our_fund_avg_return_pct": our_return,
        "gap_vs_category_bps":     gap_bps,
        "best_peer":               peers[0] if peers else None,
        "worst_peer":              peers[-1] if peers else None,
        "peer_count":              len(peers),
    }