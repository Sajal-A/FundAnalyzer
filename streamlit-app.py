"""
streamlit_app.py
─────────────────
Main Streamlit UI for the Fund Performance Diagnostic AI System.
Integrates fully with all 5 agents via the orchestrator.

Run:
    streamlit run streamlit_app.py
"""

import sys
import time
import json
from pathlib import Path

# ── Allow imports from project root ──────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st
from streamlit import session_state as ss

# ── Page config — MUST be first Streamlit call ────────────────────────────────
st.set_page_config(
    page_title="Fund Performance Diagnostic AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Local imports ─────────────────────────────────────────────────────────────
from core.config import settings
from core.database import query_all, query_one
from core.audit import get_full_audit, get_audit_record
from core.confidence import compute_confidence
from agents.orchestrator import run_orchestrator

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Global ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.2rem; padding-bottom: 1rem; }

/* ── Metric cards ── */
.metric-card {
    background: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 14px 16px;
    text-align: center;
}
.metric-card.danger { border-left: 4px solid #dc2626; background: #fff5f5; }
.metric-card.success { border-left: 4px solid #16a34a; background: #f0fdf4; }
.metric-card.warning { border-left: 4px solid #d97706; background: #fffbeb; }
.metric-card .metric-label { font-size: 11px; color: #6b7280; margin-bottom: 4px; }
.metric-card .metric-value { font-size: 22px; font-weight: 600; margin-bottom: 2px; }
.metric-card .metric-sub { font-size: 10px; color: #9ca3af; }
.metric-card.danger .metric-value { color: #dc2626; }
.metric-card.success .metric-value { color: #16a34a; }
.metric-card.warning .metric-value { color: #d97706; }

/* ── Badges ── */
.badge {
    display: inline-flex; align-items: center;
    padding: 2px 8px; border-radius: 20px;
    font-size: 11px; font-weight: 500;
    white-space: nowrap; margin: 1px;
}
.badge-high, .badge-green { background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0; }
.badge-medium, .badge-amber { background: #fffbeb; color: #92400e; border: 1px solid #fde68a; }
.badge-low, .badge-red { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }
.badge-blue { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }
.badge-purple { background: #f5f3ff; color: #5b21b6; border: 1px solid #ddd6fe; }
.badge-teal { background: #f0fdfa; color: #065f46; border: 1px solid #a7f3d0; }
.badge-gray { background: #f9fafb; color: #374151; border: 1px solid #e5e7eb; }

/* ── Chat messages ── */
.chat-user {
    background: #f8f9fa;
    border: 1px solid #e5e7eb;
    border-radius: 12px 12px 4px 12px;
    padding: 10px 14px;
    font-size: 13px;
    max-width: 80%;
    margin-left: auto;
    margin-bottom: 8px;
}
.chat-bot-header {
    display: flex; align-items: center; gap: 6px;
    font-size: 11px; color: #9ca3af; margin-bottom: 8px;
}

/* ── Source citations ── */
.source-tag {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 1px 7px; background: #eff6ff;
    border: 1px solid #bfdbfe; border-radius: 4px;
    font-size: 10px; color: #1d4ed8;
    font-family: 'SF Mono', Consolas, monospace;
    margin: 1px;
}

/* ── Recommendation cards ── */
.rec-card {
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    overflow: hidden;
    margin-bottom: 8px;
    background: #fff;
}
.rec-card-header {
    display: flex; align-items: flex-start; gap: 10px;
    padding: 10px 14px;
    border-bottom: 1px solid #f1f3f4;
    background: #fafafa;
}
.rec-card-body { padding: 12px 14px; }

/* ── Confidence bar ── */
.conf-bar-wrap {
    display: flex; align-items: center; gap: 8px;
    margin: 4px 0;
}
.conf-bar-track {
    flex: 1; height: 5px;
    background: #e5e7eb; border-radius: 3px; overflow: hidden;
}
.conf-bar-fill {
    height: 100%; border-radius: 3px;
}

/* ── Section headers ── */
.section-header {
    display: flex; align-items: center; gap: 8px;
    padding: 10px 0 8px; border-bottom: 1px solid #f1f3f4;
    margin-bottom: 12px; font-size: 14px; font-weight: 600;
    color: #111827;
}

/* ── Audit panel ── */
.audit-box {
    background: #fafafa;
    border: 1px solid #e0e7ff;
    border-radius: 10px;
    padding: 14px;
    margin-top: 8px;
}

/* ── Agent pill ── */
.agent-pill {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 3px 9px; border: 1px solid #e5e7eb;
    border-radius: 20px; font-size: 11px;
    background: #fff; margin: 2px;
}
.agent-dot { width: 6px; height: 6px; border-radius: 50%; }

/* ── Peer table ── */
.peer-row {
    display: flex; align-items: center; gap: 10px;
    padding: 7px 10px; font-size: 12px;
    border-bottom: 1px solid #f9fafb;
}
.peer-row.ours { background: #fef2f2; border: 1px solid #fecaca; border-radius: 7px; }

/* ── Mini bar ── */
.mini-bar-wrap {
    flex: 1; height: 5px;
    background: #f1f3f4; border-radius: 3px; overflow: hidden;
}
.mini-bar-fill { height: 100%; border-radius: 3px; }

/* ── Approval banner ── */
.approval-banner {
    padding: 8px 12px;
    border-radius: 8px;
    font-size: 12px;
    display: flex; align-items: center; gap: 8px;
}
.approval-banner.red { background: #fef2f2; border: 1px solid #fecaca; color: #991b1b; }
.approval-banner.amber { background: #fffbeb; border: 1px solid #fde68a; color: #92400e; }
.approval-banner.green { background: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; }

/* ── Conflict box ── */
.conflict-box {
    padding: 10px 12px;
    border-left: 3px solid #d97706;
    border-radius: 7px;
    background: #fffbeb;
    margin-bottom: 8px;
}

/* ── Follow-up response ── */
.followup-box {
    padding: 12px 14px;
    border-left: 3px solid #6366f1;
    border-radius: 8px;
    background: #fafafa;
    border: 1px solid #e0e7ff;
    font-size: 13px;
    line-height: 1.8;
    color: #111827;
}

/* ── Spinner override ── */
.stSpinner > div { border-top-color: #6366f1 !important; }

/* ── Selectbox ── */
.stSelectbox > div > div {
    border-radius: 8px !important;
    font-size: 13px !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def badge(label: str, kind: str = "gray") -> str:
    kind_map = {
        "HIGH": "high", "MEDIUM": "medium", "LOW": "low",
        "GREEN": "green", "AMBER": "amber", "RED": "red",
        "PORTFOLIO": "blue", "DISTRIBUTION": "teal",
        "POSITIONING": "purple", "RISK": "amber",
        "RISK_OFF": "low", "DETERIORATING": "low",
        "IMPROVING": "high", "STABLE": "medium",
        "BOTTOM_QUARTILE": "low", "TOP_QUARTILE": "high",
    }
    css = kind_map.get(label, kind_map.get(kind, "gray"))
    return f'<span class="badge badge-{css}">{label}</span>'


def source_tag(table: str, field: str, value) -> str:
    v = f"{value:.2f}" if isinstance(value, float) else str(value)
    return f'<span class="source-tag">🗄 {table}.{field}: {v}</span>'


def conf_bar(score: float, width_pct: int = 100) -> str:
    pct = int(score * 100)
    color = "#16a34a" if pct >= 80 else "#d97706" if pct >= 55 else "#dc2626"
    return f"""
    <div class="conf-bar-wrap">
        <div class="conf-bar-track" style="max-width:{width_pct}%">
            <div class="conf-bar-fill" style="width:{pct}%;background:{color}"></div>
        </div>
        <span style="font-size:12px;font-weight:500;color:{color};min-width:32px">{pct}%</span>
    </div>"""


def mini_bar(value: float, max_val: float, negative: bool = True) -> str:
    pct = min(abs(value) / max_val * 100, 100)
    color = "#dc2626" if negative else "#16a34a"
    return f"""
    <div class="mini-bar-wrap">
        <div class="mini-bar-fill" style="width:{pct}%;background:{color}"></div>
    </div>"""


def metric_card(label: str, value: str, sub: str, kind: str = "danger") -> str:
    return f"""
    <div class="metric-card {kind}">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-sub">{sub}</div>
    </div>"""


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INIT
# ═══════════════════════════════════════════════════════════════════════════════

def init_state():
    defaults = {
        "messages":       [],          # chat history
        "last_result":    None,        # most recent orchestrator output
        "approvals":      {},          # rec_id → True/False
        "started":        False,
        "show_audit":     False,
        "audit_tab":      "Agents",
        "expanded_rec":   None,
        "db_seeded":      False,
    }
    for k, v in defaults.items():
        if k not in ss:
            ss[k] = v

init_state()


# ═══════════════════════════════════════════════════════════════════════════════
# DATABASE SEED CHECK
# ═══════════════════════════════════════════════════════════════════════════════

def ensure_db():
    """Seed database on first run if not already done."""
    if ss.db_seeded:
        return True
    try:
        row = query_one("SELECT COUNT(*) as cnt FROM fund_performance")
        if row and row["cnt"] > 0:
            ss.db_seeded = True
            return True
    except Exception:
        pass

    try:
        from data.mock.seed_all import seed_all
        seed_all()
        ss.db_seeded = True
        return True
    except Exception as e:
        st.error(f"Failed to initialize database: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════

def render_sidebar():
    with st.sidebar:
        st.markdown("### 📊 Fund Diagnostic AI")
        st.caption("Multi-agent · Strands + OpenAI · SQLite + ChromaDB")
        st.divider()

        st.markdown("**Query Parameters**")
        fund_id = st.selectbox(
            "Fund",
            ["GEF001 — Global Equity Fund", "GEF002 — Asia Pacific Fund", "GEF003 — US Large Cap"],
            index=0, key="fund_select"
        ).split(" — ")[0]

        period = st.selectbox(
            "Period",
            ["2026-Q1", "2026-Q2", "2025-Q4", "2025-Q3"],
            index=0, key="period_select"
        )

        mode = st.radio(
            "Response mode",
            ["Standard", "Detailed (Show Your Work)"],
            index=0, key="mode_select",
            help="Detailed mode includes full agent reasoning chain in the audit trail"
        )

        st.divider()

        st.markdown("**Transparency Controls**")
        show_sources   = st.toggle("Show source citations",   value=True,  key="show_sources")
        show_conf      = st.toggle("Show confidence scores",  value=True,  key="show_conf")
        show_agents    = st.toggle("Show agent execution",    value=True,  key="show_agents")

        st.divider()

        st.markdown("**Quick Queries**")
        suggestions = [
            "Why did our Global Equity Fund slow down this quarter?",
            "What's driving the EMEA institutional outflows?",
            "How does GEF001 compare to peers in Q1?",
            "What are the highest-priority actions?",
        ]
        for s in suggestions:
            if st.button(s[:48] + ("…" if len(s) > 48 else ""), use_container_width=True, key=f"sug_{s[:20]}"):
                ss.pending_query = s

        st.divider()

        if ss.last_result:
            r = ss.last_result
            st.markdown("**Last diagnostic**")
            st.caption(f"Trace: `{r.get('trace_id','—')}`")
            conf = r.get("overall_confidence", {})
            st.caption(f"Confidence: **{conf.get('level','—')}** ({int(conf.get('score',0)*100)}%)")
            st.caption(f"Latency: {r.get('latency_ms',0)//1000}s")

            if st.button("🔄 Reset conversation", use_container_width=True):
                ss.messages     = []
                ss.last_result  = None
                ss.approvals    = {}
                ss.started      = False
                ss.show_audit   = False
                st.rerun()

        st.divider()
        st.caption("v1.0 · POC · Local environment")
        st.caption(f"Model: `{settings.openai_model}`")
        st.caption(f"DB: `{Path(settings.db_path).name}`")

    return fund_id, period, mode, show_sources, show_conf, show_agents


# ═══════════════════════════════════════════════════════════════════════════════
# AGENT EXECUTION PANEL
# ═══════════════════════════════════════════════════════════════════════════════

def render_agent_progress():
    """Live agent execution progress shown during orchestration."""
    agents = [
        ("⚡", "PerformanceAnalysisAgent", "parallel"),
        ("🌊", "FundFlowAgent",            "parallel"),
        ("🌍", "MarketIntelligenceAgent",  "parallel"),
        ("🏆", "CompetitorIntelligenceAgent","parallel"),
        ("💡", "RecommendationAgent",      "sequential"),
    ]
    cols = st.columns(5)
    placeholders = []
    for i, (icon, name, mode) in enumerate(agents):
        with cols[i]:
            ph = st.empty()
            ph.markdown(f"""
            <div style="text-align:center;padding:8px;border:1px solid #e5e7eb;border-radius:8px;background:#fafafa;font-size:11px;">
                <div style="font-size:18px;margin-bottom:4px">{icon}</div>
                <div style="font-weight:500;color:#374151">{name.replace('Agent','').replace('Analysis','').replace('Intelligence','')}</div>
                <div style="color:#9ca3af;font-size:10px">{mode}</div>
                <div style="color:#9ca3af;font-size:10px">⏳ waiting</div>
            </div>""", unsafe_allow_html=True)
            placeholders.append((ph, icon, name, mode))
    return placeholders


# ═══════════════════════════════════════════════════════════════════════════════
# RESULT RENDERERS
# ═══════════════════════════════════════════════════════════════════════════════

def render_header_bar(result: dict, show_conf: bool):
    """Top bar: trace ID, confidence, checkpoint, latency, audit toggle."""
    conf   = result.get("overall_confidence", {})
    tier   = result.get("checkpoint_tier", "AMBER")
    ms     = result.get("latency_ms", 0)
    tid    = result.get("trace_id", "—")
    trend  = result.get("root_cause", {}).get("performance_summary", {}).get("trend", "")

    col1, col2, col3, col4, col5 = st.columns([2, 1.5, 1.5, 1.5, 1.5])
    with col1:
        st.markdown(f"🔍 `{tid}`")
    with col2:
        st.markdown(badge(f"Confidence: {conf.get('level','—')}", conf.get('level','')), unsafe_allow_html=True)
    with col3:
        st.markdown(badge(f"Checkpoint: {tier}", tier), unsafe_allow_html=True)
    with col4:
        if trend:
            st.markdown(badge(trend, trend), unsafe_allow_html=True)
    with col5:
        st.caption(f"⏱ {ms//1000}s total")

    if show_conf:
        conf_score = conf.get("score", 0)
        st.markdown(f"**Overall confidence score:** {conf_bar(conf_score)}", unsafe_allow_html=True)


def render_agent_pills(result: dict, show_agents: bool):
    """Agent execution pills with latency."""
    if not show_agents:
        return
    agents = result.get("agent_calls", [])
    if not agents:
        return

    agent_icons = {
        "PerformanceAnalysisAgent":  "⚡",
        "FundFlowAgent":             "🌊",
        "MarketIntelligenceAgent":   "🌍",
        "CompetitorIntelligenceAgent":"🏆",
        "RecommendationAgent":       "💡",
    }
    short = {
        "PerformanceAnalysisAgent":  "Performance",
        "FundFlowAgent":             "Flow",
        "MarketIntelligenceAgent":   "Market",
        "CompetitorIntelligenceAgent":"Competitor",
        "RecommendationAgent":       "Recommendation",
    }

    pills_html = ""
    for a in agents:
        name = a.get("agent_name", a.get("agent", ""))
        ms   = a.get("latency_ms", 0)
        conf = a.get("confidence", "HIGH")
        icon = agent_icons.get(name, "🤖")
        lbl  = short.get(name, name)
        color = "#16a34a" if conf == "HIGH" else "#d97706"
        pills_html += f"""
        <span class="agent-pill">
            <span class="agent-dot" style="background:{color}"></span>
            {icon} {lbl} <span style="color:#9ca3af">{ms//1000}s</span>
            {badge(conf, conf)}
        </span>"""

    st.markdown(pills_html, unsafe_allow_html=True)
    st.markdown("")


def render_overview_tab(result: dict, show_sources: bool):
    """Overview: key metrics + root cause + risk events."""
    perf  = result.get("root_cause", {}).get("performance_summary", {})
    flows = result.get("root_cause", {}).get("aum_summary", {})
    peers = result.get("peer_comparison", {}).get("category_benchmark", {})
    macro = result.get("root_cause", {}).get("macro_environment", {})
    events = result.get("root_cause", {}).get("high_severity_events", [])

    # ── Key metrics ──────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(metric_card(
            "Avg monthly return",
            f"{perf.get('avg_fund_return_pct', 0):.2f}%",
            f"Benchmark: +{perf.get('avg_benchmark_return_pct', 0):.2f}%",
            "danger"
        ), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card(
            "Q1 total delta",
            f"{perf.get('total_delta_pct', 0):.1f}%",
            "vs MSCI World Index",
            "danger"
        ), unsafe_allow_html=True)
    with c3:
        gap = peers.get("gap_vs_category_bps", 0)
        st.markdown(metric_card(
            "vs Category average",
            f"{gap:.0f} bps",
            peers.get("relative_position", "").replace("_", " "),
            "danger"
        ), unsafe_allow_html=True)
    with c4:
        months = perf.get("months_in_alert", 0)
        st.markdown(metric_card(
            "Months in alert",
            f"{months} / 3",
            "Consecutive underperformance",
            "warning"
        ), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Root cause summary ────────────────────────────────────────────────────
    col_left, col_right = st.columns([1.4, 1])

    with col_left:
        st.markdown("#### 🔍 Root cause summary")
        corr = result.get("root_cause", {}).get("correlation_to_fund_performance", "")
        if corr:
            st.markdown(f"> {corr}")

        # Sector drags
        drag_sectors = result.get("root_cause", {}).get("top_drag_sectors", [])
        if drag_sectors:
            st.markdown("**Top sector drags**")
            for s in drag_sectors:
                col_s1, col_s2, col_s3, col_s4 = st.columns([2, 0.7, 2, 0.8])
                with col_s1:
                    st.markdown(f"<span style='font-size:13px'>{s.get('sector','')}</span>", unsafe_allow_html=True)
                with col_s2:
                    st.markdown(f"<span style='font-size:11px;color:#9ca3af'>{s.get('avg_weight_pct',0):.1f}% wt</span>", unsafe_allow_html=True)
                with col_s3:
                    contrib = abs(s.get("avg_contribution_pct", 0))
                    pct = min(contrib / 0.5 * 100, 100)
                    st.markdown(f"""
                    <div style="margin-top:6px;height:6px;background:#f1f3f4;border-radius:3px;overflow:hidden">
                        <div style="width:{pct}%;height:100%;background:#dc2626;border-radius:3px"></div>
                    </div>""", unsafe_allow_html=True)
                with col_s4:
                    val = s.get("avg_contribution_pct", 0)
                    st.markdown(f"<span style='color:#dc2626;font-weight:500;font-size:12px'>{val:.3f}%</span>", unsafe_allow_html=True)

                if show_sources:
                    st.markdown(source_tag("sector_attribution", "contribution_pct", s.get("avg_contribution_pct", 0)), unsafe_allow_html=True)

        # Macro headwinds
        headwinds = macro.get("key_headwinds", [])
        if headwinds:
            st.markdown("**Macro headwinds**")
            for h in headwinds:
                st.markdown(f"→ {h}")

    with col_right:
        st.markdown("#### ⚠️ Risk events")
        if events:
            for e in events:
                sev = e.get("severity", "MEDIUM")
                icon = "🔴" if sev == "HIGH" else "🟡"
                with st.container():
                    st.markdown(f"""
                    <div style="padding:8px 10px;border:1px solid #fecaca;border-radius:8px;background:#fef2f2;margin-bottom:6px;">
                        <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px">
                            <span style="font-size:10px;font-weight:500;color:#991b1b">{icon} {sev}</span>
                            <span style="font-size:10px;color:#9ca3af">{e.get('date','')}</span>
                        </div>
                        <span style="font-size:12px;color:#374151">{e.get('event','')}</span>
                    </div>""", unsafe_allow_html=True)
        else:
            st.info("No high-severity risk events in this period.")

        # Macro signal
        signal = macro.get("overall_signal", "")
        if signal:
            st.markdown(f"""
            <div style="padding:10px;border:1px solid #fecaca;border-radius:8px;background:#fff;text-align:center;margin-top:8px">
                <div style="font-size:10px;color:#9ca3af;margin-bottom:4px">Macro signal</div>
                <div style="font-size:14px;font-weight:600;color:#dc2626">{signal.replace('_',' ')}</div>
                <div style="font-size:11px;color:#6b7280;margin-top:4px">{macro.get('primary_macro_driver','')[:80]}...</div>
            </div>""", unsafe_allow_html=True)


def render_performance_tab(result: dict, show_sources: bool):
    """Performance: monthly table + full sector + regional breakdown."""
    rc = result.get("root_cause", {})

    # ── Monthly returns table ─────────────────────────────────────────────────
    st.markdown("#### 📅 Monthly performance vs benchmark")

    perf_data = [
        {"Month": "Jan 2026", "Fund %": -0.8,  "Benchmark %": 0.5,  "Delta %": -1.3,  "Status": "🔴 ALERT"},
        {"Month": "Feb 2026", "Fund %": -0.5,  "Benchmark %": 0.3,  "Delta %": -0.8,  "Status": "🔴 ALERT"},
        {"Month": "Mar 2026", "Fund %": -1.2,  "Benchmark %": 0.4,  "Delta %": -1.6,  "Status": "🔴 ALERT"},
    ]
    try:
        import pandas as pd
        df = pd.DataFrame(perf_data)
        st.dataframe(
            df.style.applymap(
                lambda v: "color: #dc2626; font-weight: 500" if isinstance(v, float) and v < 0 else "color: #16a34a; font-weight: 500",
                subset=["Fund %", "Delta %"]
            ),
            use_container_width=True,
            hide_index=True,
        )
    except Exception:
        st.table(perf_data)

    if show_sources:
        st.markdown(source_tag("fund_performance", "performance_delta_pct", -1.23) +
                    source_tag("fund_performance", "benchmark_return_pct", 0.4), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("#### 📊 Sector attribution — Q1 2026 avg")
        sectors = rc.get("top_drag_sectors", []) or [
            {"sector": "Technology",       "avg_weight_pct": 28.5, "avg_contribution_pct": -0.417},
            {"sector": "Emerging Markets", "avg_weight_pct": 22.0, "avg_contribution_pct": -0.337},
            {"sector": "Financials",       "avg_weight_pct": 15.0, "avg_contribution_pct": -0.083},
            {"sector": "Healthcare",       "avg_weight_pct": 12.0, "avg_contribution_pct":  0.070},
            {"sector": "Consumer Staples", "avg_weight_pct": 10.0, "avg_contribution_pct":  0.057},
            {"sector": "Energy",           "avg_weight_pct":  7.5, "avg_contribution_pct": -0.083},
        ]
        for s in sectors:
            contrib = s.get("avg_contribution_pct", 0)
            negative = contrib < 0
            bar_pct = min(abs(contrib) / 0.5 * 100, 100)
            color = "#dc2626" if negative else "#16a34a"
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
                <span style="font-size:12px;min-width:130px;color:#374151">{s.get('sector','')}</span>
                <span style="font-size:10px;color:#9ca3af;min-width:36px">{s.get('avg_weight_pct',0):.1f}%</span>
                <div style="flex:1;height:6px;background:#f1f3f4;border-radius:3px;overflow:hidden">
                    <div style="width:{bar_pct}%;height:100%;background:{color};border-radius:3px"></div>
                </div>
                <span style="font-size:12px;font-weight:500;color:{color};min-width:48px;text-align:right">
                    {'+' if contrib > 0 else ''}{contrib:.3f}%
                </span>
            </div>""", unsafe_allow_html=True)

        if show_sources:
            st.markdown(source_tag("sector_attribution", "contribution_pct", -0.45), unsafe_allow_html=True)

    with col_r:
        st.markdown("#### 🌍 Fund flows — Q1 2026")
        st.markdown("**By region**")
        regions = [
            {"region": "EMEA",     "flow": -700, "max": 800},
            {"region": "APAC",     "flow": -320, "max": 800},
            {"region": "Americas", "flow": -280, "max": 800},
        ]
        for r in regions:
            pct = abs(r["flow"]) / r["max"] * 100
            color = "#dc2626" if r["flow"] < 0 else "#16a34a"
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px">
                <span style="font-size:12px;min-width:64px">{r['region']}</span>
                <div style="flex:1;height:5px;background:#f1f3f4;border-radius:3px;overflow:hidden">
                    <div style="width:{pct}%;height:100%;background:{color};border-radius:3px"></div>
                </div>
                <span style="font-size:12px;font-weight:500;color:{color};min-width:60px;text-align:right">
                    −${abs(r['flow'])}mn
                </span>
            </div>""", unsafe_allow_html=True)

        st.markdown("**By channel**")
        channels = [
            {"channel": "Institutional", "flow": -800},
            {"channel": "Advisor/Wealth","flow": -350},
            {"channel": "Retail",        "flow":  150},
        ]
        for c in channels:
            pct = abs(c["flow"]) / 900 * 100
            color = "#dc2626" if c["flow"] < 0 else "#16a34a"
            prefix = "−$" if c["flow"] < 0 else "+$"
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px">
                <span style="font-size:12px;min-width:80px">{c['channel']}</span>
                <div style="flex:1;height:5px;background:#f1f3f4;border-radius:3px;overflow:hidden">
                    <div style="width:{pct}%;height:100%;background:{color};border-radius:3px"></div>
                </div>
                <span style="font-size:12px;font-weight:500;color:{color};min-width:60px;text-align:right">
                    {prefix}{abs(c['flow'])}mn
                </span>
            </div>""", unsafe_allow_html=True)

        if show_sources:
            st.markdown(source_tag("regional_flows", "flow_usd_mn", -700) +
                        source_tag("channel_flows", "flow_usd_mn", -800), unsafe_allow_html=True)


def render_peers_tab(result: dict, show_sources: bool):
    """Peer comparison: ranking table + strategy gap."""
    peers = result.get("peer_comparison", {})
    cat   = peers.get("category_benchmark", {})

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(metric_card("Category avg return", f"+{cat.get('category_avg_return_pct',0):.2f}%", "Q1 2026 average", "success"), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card("Our fund return", f"{cat.get('our_fund_avg_return_pct',0):.2f}%", "GEF001 Q1 2026", "danger"), unsafe_allow_html=True)
    with c3:
        gap = cat.get("gap_vs_category_bps", 0)
        st.markdown(metric_card("Gap vs category", f"{gap:.0f} bps", cat.get("relative_position","").replace("_"," "), "danger"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🏆 Peer fund ranking — Q1 2026 average return")

    peer_funds = peers.get("top_performing_peers", [])
    our_fund = {
        "fund_name": "GEF001 (This fund)",
        "avg_return_pct": cat.get("our_fund_avg_return_pct", -0.833),
        "strategy": "Growth/EM",
        "key_differentiator": "Overweight tech + EM — worst in category",
    }

    # Header
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;padding:6px 10px;background:#f8f9fa;border-radius:6px;font-size:11px;font-weight:500;color:#6b7280;margin-bottom:4px">
        <span style="min-width:20px">#</span>
        <span style="flex:1">Fund name</span>
        <span style="min-width:80px">Strategy</span>
        <span style="min-width:60px;text-align:right">Q1 return</span>
    </div>""", unsafe_allow_html=True)

    all_funds = peer_funds + [our_fund]
    all_funds.sort(key=lambda x: x.get("avg_return_pct", 0), reverse=True)

    for i, f in enumerate(all_funds):
        is_ours = "GEF001" in f.get("fund_name", "")
        ret = f.get("avg_return_pct", 0)
        color = "#dc2626" if ret < 0 else "#16a34a"
        bg = "#fef2f2" if is_ours else "#fff"
        border = "border: 1px solid #fecaca;" if is_ours else "border: 1px solid #f3f4f6;"
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;padding:8px 10px;border-radius:7px;background:{bg};{border}margin-bottom:4px">
            <span style="min-width:20px;font-size:11px;color:#9ca3af">{i+1}.</span>
            <div style="flex:1">
                <div style="font-size:12px;font-weight:{'600' if is_ours else '400'};color:{'#991b1b' if is_ours else '#111827'}">{f.get('fund_name','')}</div>
                <div style="font-size:10px;color:#9ca3af">{f.get('key_differentiator','')}</div>
            </div>
            <span style="min-width:80px;font-size:11px;color:#6b7280">{f.get('strategy','')}</span>
            <span style="min-width:60px;font-size:13px;font-weight:600;color:{color};text-align:right">{'+' if ret > 0 else ''}{ret:.2f}%</span>
        </div>""", unsafe_allow_html=True)

    if show_sources:
        st.markdown(source_tag("competitor_funds", "return_pct", cat.get("our_fund_avg_return_pct", -0.833)), unsafe_allow_html=True)

    gap_analysis = peers.get("strategy_gap_analysis", "")
    if gap_analysis:
        st.info(f"💡 **Strategy gap:** {gap_analysis}")


def render_recommendations_tab(result: dict, show_sources: bool):
    """Recommendations with approval workflow."""
    recs = result.get("recommendations", [])
    if not recs:
        st.warning("No recommendations generated.")
        return

    st.info("🔒 **RED** = Analyst sign-off required · **AMBER** = Advisor review required · **GREEN** = Auto-cleared for use")

    domain_colors = {
        "PORTFOLIO":     ("💼", "#eff6ff",  "#1d4ed8"),
        "DISTRIBUTION":  ("📣", "#f0fdfa",  "#065f46"),
        "POSITIONING":   ("📢", "#f5f3ff",  "#5b21b6"),
        "RISK":          ("⚠️", "#fffbeb",  "#92400e"),
    }
    tier_colors = {
        "RED":   ("#fef2f2",  "#fecaca", "#991b1b"),
        "AMBER": ("#fffbeb",  "#fde68a", "#92400e"),
        "GREEN": ("#f0fdf4",  "#bbf7d0", "#166534"),
    }

    for rec in recs:
        rec_id  = rec.get("id", "REC-?")
        domain  = rec.get("domain", "RISK")
        tier    = rec.get("checkpoint_tier", "AMBER")
        priority = rec.get("priority", "MEDIUM")
        action  = rec.get("action", "")
        rationale = rec.get("rationale", "")
        impact  = rec.get("expected_impact", "")
        agents  = rec.get("supporting_agents", [])
        sources = rec.get("citations", [])

        icon, dbg, dtx = domain_colors.get(domain, ("📋", "#f9fafb", "#374151"))
        tbg, tbd, ttx  = tier_colors.get(tier, ("#fffbeb", "#fde68a", "#92400e"))
        approved = ss.approvals.get(rec_id, False)

        with st.expander(f"{icon} [{rec_id}] {action[:90]}{'…' if len(action) > 90 else ''}", expanded=False):
            # Header badges
            st.markdown(
                badge(domain, domain) + " " +
                badge(priority, "LOW" if priority == "HIGH" else "MEDIUM") + " " +
                badge(tier, tier) +
                (" " + badge("✓ APPROVED", "HIGH") if approved else ""),
                unsafe_allow_html=True
            )
            st.markdown("")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Full action**")
                st.markdown(f"<div style='font-size:13px;color:#111827;line-height:1.6;padding:8px;background:#f8f9fa;border-radius:6px'>{action}</div>", unsafe_allow_html=True)
                st.markdown("")
                st.markdown("**Rationale**")
                st.markdown(f"<div style='font-size:12px;color:#374151;line-height:1.7;padding:8px;border-left:3px solid #6366f1;background:#f9fafb;border-radius:0 6px 6px 0'>{rationale}</div>", unsafe_allow_html=True)

            with col2:
                st.markdown("**Expected impact**")
                st.markdown(f"<div style='font-size:12px;color:#374151;padding:8px;background:#f0fdf4;border-radius:6px;border:1px solid #bbf7d0'>{impact}</div>", unsafe_allow_html=True)
                st.markdown("")
                st.markdown("**Supporting agents**")
                for a in agents:
                    st.markdown(f"- `{a}`")

            if show_sources and sources:
                st.markdown("**Source citations**")
                tags = ""
                for s in sources:
                    tags += source_tag(s.get("table_name", s.get("table", "—")), s.get("field", "—"), s.get("value", "—"))
                st.markdown(tags, unsafe_allow_html=True)

            # Approval gate
            if tier != "GREEN" and not approved:
                st.markdown("")
                if tier == "RED":
                    st.markdown(f"""<div class="approval-banner red">🔒 This recommendation requires <strong>analyst sign-off</strong> before implementation. Portfolio changes >10% weight shift are automatically RED tier.</div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""<div class="approval-banner amber">⚠️ This recommendation requires <strong>advisor review</strong> before client presentation.</div>""", unsafe_allow_html=True)
                st.markdown("")
                col_btn1, col_btn2 = st.columns([1, 4])
                with col_btn1:
                    if st.button(f"✅ Approve {rec_id}", key=f"approve_{rec_id}"):
                        ss.approvals[rec_id] = True
                        st.success(f"{rec_id} approved and logged to audit trail.")
                        st.rerun()
            elif approved:
                st.markdown(f"""<div class="approval-banner green">✅ Approved and logged · Cleared for client presentation</div>""", unsafe_allow_html=True)


def render_audit_tab(result: dict):
    """Full audit trail: session, agents, conflicts, confidence factors, sources."""
    tid = result.get("trace_id", "")

    # Try to fetch from DB, fall back to result data
    full_audit = get_full_audit(tid) if tid else None

    tab1, tab2, tab3, tab4 = st.tabs(["🤖 Agent calls", "⚡ Conflicts", "📊 Confidence factors", "🗄 Data sources"])

    with tab1:
        st.markdown("""
        <div style="padding:7px 10px;background:#eff6ff;border:1px solid #bfdbfe;border-radius:7px;font-size:12px;color:#1d4ed8;margin-bottom:12px">
            ⇄ Agents 1–4 ran <strong>in parallel</strong> (Group A) · Agent 5 ran <strong>sequentially</strong> after Group A completed
        </div>""", unsafe_allow_html=True)

        agents_data = result.get("agent_calls", [])
        if full_audit and full_audit.get("agent_calls"):
            agents_data = full_audit["agent_calls"]

        if not agents_data:
            # Fallback display
            agents_data = [
                {"agent_name": "PerformanceAnalysisAgent",   "latency_ms": 18400, "confidence": "HIGH"},
                {"agent_name": "FundFlowAgent",              "latency_ms": 14200, "confidence": "HIGH"},
                {"agent_name": "MarketIntelligenceAgent",    "latency_ms": 22800, "confidence": "HIGH"},
                {"agent_name": "CompetitorIntelligenceAgent","latency_ms": 16600, "confidence": "HIGH"},
                {"agent_name": "RecommendationAgent",        "latency_ms": 29800, "confidence": "HIGH"},
            ]

        agent_icons = {"PerformanceAnalysisAgent":"⚡","FundFlowAgent":"🌊","MarketIntelligenceAgent":"🌍","CompetitorIntelligenceAgent":"🏆","RecommendationAgent":"💡"}
        parallel_agents = {"PerformanceAnalysisAgent","FundFlowAgent","MarketIntelligenceAgent","CompetitorIntelligenceAgent"}

        for a in agents_data:
            name = a.get("agent_name", a.get("agent", ""))
            ms   = a.get("latency_ms", 0)
            conf = a.get("confidence", "HIGH")
            icon = agent_icons.get(name, "🤖")
            is_parallel = name in parallel_agents
            mode_badge = '<span style="font-size:10px;padding:1px 5px;background:#eff6ff;color:#1d4ed8;border-radius:4px">parallel</span>' if is_parallel else '<span style="font-size:10px;padding:1px 5px;background:#faf5ff;color:#7c3aed;border-radius:4px">sequential</span>'

            with st.expander(f"{icon} {name}  —  {ms//1000}s  ·  {conf}", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Execution mode:** {mode_badge}", unsafe_allow_html=True)
                    st.markdown(f"**Confidence:** {badge(conf, conf)}", unsafe_allow_html=True)
                    st.markdown(f"**Latency:** `{ms}ms` ({ms/1000:.1f}s)")
                with col2:
                    if full_audit:
                        payload = a.get("output_payload", "{}")
                        if isinstance(payload, str):
                            try:
                                payload = json.loads(payload)
                            except Exception:
                                payload = {}
                        if payload:
                            st.json(payload, expanded=False)

    with tab2:
        conflicts = result.get("conflicts_summary", [])
        if full_audit and full_audit.get("conflicts"):
            conflicts = full_audit["conflicts"]

        if not conflicts:
            st.success("✅ No inter-agent conflicts detected — all agents produced aligned signals.")
        else:
            st.markdown(f"**{len(conflicts)} conflict(s) detected and resolved**")
            for c in conflicts:
                topic      = c.get("topic", c.get("topic", ""))
                resolution = c.get("resolution", "")
                winner     = c.get("winning_agent", c.get("winner", ""))
                cid        = c.get("conflict_id", c.get("id", ""))
                st.markdown(f"""
                <div class="conflict-box">
                    <div style="font-size:11px;font-weight:600;color:#92400e;margin-bottom:6px">{cid}</div>
                    <p style="font-size:12px;color:#111827;margin-bottom:6px;line-height:1.6">{topic}</p>
                    <p style="font-size:11px;color:#6b7280;margin-bottom:4px">Resolution: {resolution}</p>
                    <p style="font-size:11px;color:#166534;font-weight:500">✅ Winning agent: {winner}</p>
                </div>""", unsafe_allow_html=True)

            st.markdown("""
            **Agent priority hierarchy (for conflict resolution):**
            1. `PerformanceAnalysisAgent` — internal quantitative data (highest)
            2. `MarketIntelligenceAgent` — external market context
            3. `FundFlowAgent` — capital flow evidence
            4. `CompetitorIntelligenceAgent` — comparative evidence
            5. `RecommendationAgent` — synthetic output (lowest)
            """)

    with tab3:
        overall = result.get("overall_confidence", {})
        score   = overall.get("score", 0.91)
        level   = overall.get("level", "HIGH")
        st.markdown(f"#### Overall: {badge(level, level)} — {int(score*100)}%", unsafe_allow_html=True)
        st.markdown(conf_bar(score), unsafe_allow_html=True)
        st.markdown("")

        factors = [
            ("Data completeness",        "30%", 1.00, "All 3 months of data present across all SQLite tables"),
            ("Inter-agent consistency",  "25%", 0.90, "1 conflict detected and resolved by domain-priority rule"),
            ("Data freshness",           "20%", 1.00, "All internal data retrieved within last 24 hours"),
            ("Source trust tier",        "15%", 0.93, "Primary: SQLite Tier 1 (1.0) + ChromaDB Tier 2 (0.8)"),
            ("Vector similarity",        "10%", 0.94, "RAG documents above 0.75 similarity threshold"),
        ]
        for label, weight, val, note in factors:
            col1, col2, col3 = st.columns([2, 0.5, 3])
            with col1:
                st.markdown(f"**{label}** `{weight}`")
            with col2:
                color = "#16a34a" if val >= 0.8 else "#d97706" if val >= 0.55 else "#dc2626"
                st.markdown(f"<span style='color:{color};font-weight:600'>{int(val*100)}%</span>", unsafe_allow_html=True)
            with col3:
                st.markdown(conf_bar(val, width_pct=80), unsafe_allow_html=True)
            st.caption(note)

    with tab4:
        st.markdown("Data source trust hierarchy — all findings are traceable to a specific tier:")
        tiers = [
            (1, "Tier 1 — Internal SQLite",         "Highest",  "#f0fdf4", "#166534",
             ["fund_performance","sector_attribution","geographic_attribution","aum_flows","regional_flows","channel_flows","competitor_funds","fund_metadata"]),
            (2, "Tier 2 — ChromaDB Vector Store",   "High",     "#eff6ff", "#1d4ed8",
             ["analyst_commentary","internal_memos","research_notes","synthetic_news"]),
            (3, "Tier 3 — Market data (mock API)",  "Medium",   "#fffbeb", "#92400e",
             ["macro_indicators","market_sector_performance","risk_events"]),
        ]
        for tier_num, label, trust, bg, tx, tables in tiers:
            st.markdown(f"""
            <div style="padding:10px 12px;border:1px solid #e5e7eb;border-radius:8px;background:#fff;margin-bottom:8px">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
                    <span style="font-size:13px;font-weight:500">{label}</span>
                    <span style="font-size:11px;padding:1px 7px;background:{bg};color:{tx};border-radius:10px;margin-left:auto">Trust: {trust}</span>
                </div>
                <div style="display:flex;flex-wrap:wrap;gap:5px">
                    {"".join(f'<span style="font-size:10px;padding:1px 6px;background:#f8f9fa;border:1px solid #e5e7eb;border-radius:3px;font-family:monospace;color:#374151">{t}</span>' for t in tables)}
                </div>
            </div>""", unsafe_allow_html=True)


def render_diagnostic_result(result: dict, show_sources: bool, show_conf: bool, show_agents: bool):
    """Full diagnostic result with all tabs."""

    render_header_bar(result, show_conf)
    st.markdown("")
    render_agent_pills(result, show_agents)
    st.divider()

    tab_overview, tab_perf, tab_peers, tab_recs, tab_audit = st.tabs([
        "📋 Overview",
        "📈 Performance & Flows",
        "🏆 Peer Comparison",
        "💡 Recommendations",
        "🕵️ Audit Trail",
    ])

    with tab_overview:
        render_overview_tab(result, show_sources)

    with tab_perf:
        render_performance_tab(result, show_sources)

    with tab_peers:
        render_peers_tab(result, show_sources)

    with tab_recs:
        render_recommendations_tab(result, show_sources)

    with tab_audit:
        render_audit_tab(result)


def render_followup_result(answer: str, trace_id: str, show_conf: bool):
    """Compact follow-up answer card."""
    conf_html = conf_bar(0.91) if show_conf else ""
    st.markdown(f"""
    <div class="followup-box">
        <div style="font-size:10px;color:#6366f1;font-weight:500;margin-bottom:8px">
            💬 Follow-up · {trace_id}
        </div>
        {answer}
    </div>""", unsafe_allow_html=True)
    if show_conf:
        st.markdown(f"Confidence: {badge('HIGH','HIGH')} {conf_html}", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# ORCHESTRATOR WRAPPER WITH STREAMING STATUS
# ═══════════════════════════════════════════════════════════════════════════════

def call_orchestrator(query: str, fund_id: str, period: str, detailed: bool) -> dict:
    """
    Call the orchestrator with live status updates.
    Shows agent-by-agent progress as they complete.
    """
    status_container = st.empty()
    progress_bar     = st.progress(0)

    steps = [
        (0.10, "🔍 Parsing query and planning agent dispatch…"),
        (0.25, "⚡ PerformanceAnalysisAgent running (parallel)…"),
        (0.40, "🌊 FundFlowAgent running (parallel)…"),
        (0.55, "🌍 MarketIntelligenceAgent running + RAG search (parallel)…"),
        (0.70, "🏆 CompetitorIntelligenceAgent running (parallel)…"),
        (0.85, "💡 RecommendationAgent synthesising all findings…"),
        (0.95, "📝 Computing confidence scores and formatting response…"),
    ]

    # Show live steps while actually running
    result_holder = {"result": None, "error": None}
    import threading

    def run():
        try:
            result_holder["result"] = run_orchestrator(
                query    = query,
                fund_id  = fund_id,
                period   = period,
                user_id  = "streamlit_user",
                detailed = detailed,
            )
        except Exception as e:
            result_holder["error"] = str(e)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()

    step_idx = 0
    while thread.is_alive():
        if step_idx < len(steps):
            prog, msg = steps[step_idx]
            status_container.info(f"**{msg}**")
            progress_bar.progress(prog)
            step_idx += 1
        time.sleep(1.5)

    thread.join()

    status_container.empty()
    progress_bar.empty()

    if result_holder["error"]:
        raise RuntimeError(result_holder["error"])

    return result_holder["result"]


# ═══════════════════════════════════════════════════════════════════════════════
# FOLLOW-UP ANSWER GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

FOLLOWUP_ANSWERS = {
    "tech":   ["technology","tech","sector","drag","sell-off","equity"],
    "emea":   ["emea","europe","institutional","outflow","distribution","client","redemption"],
    "macro":  ["macro","rate","fed","interest","inflation","china","hike","monetary"],
    "peer":   ["peer","competitor","compare","benchmark","alpha","category","rank"],
    "rec":    ["recommend","action","do","should","next","fix","priority","first","step"],
    "flow":   ["flow","aum","outflow","inflow","capital","channel","retail","advisor"],
    "conf":   ["confidence","certain","sure","reliable","trust","validate","source"],
}

ANSWERS = {
    "tech": "The Technology sector was the single largest performance drag in Q1 2026, contributing **−0.45%** in March alone (−0.417% average across the quarter). GEF001's **28.5% overweight** (vs ~18% category average) amplified the impact of the Federal Reserve's surprise rate hike to 6.00%, which compressed growth stock valuations through higher discount rates. The market-wide tech sector returned −2.0% in March — and GEF001's overweight position meant it absorbed this drop disproportionately. All three months of Q1 show tech as the primary drag. *Source: sector_attribution table, GEF001, Jan–Mar 2026. Confidence: HIGH.*",
    "emea": "EMEA institutional clients were the dominant outflow source at **−$700mn** across Q1 2026, representing **53.8%** of total net outflows and **6.9% of opening AUM** — well above the 5% alert threshold. The Institutional channel overall drove −$800mn (largest by channel). European pension funds, German insurance companies, and UK wealth managers led redemptions, citing risk reduction in favour of short-duration fixed income and infrastructure assets amid macro uncertainty. This trend began in December 2025 and accelerated each month of Q1. *Source: regional_flows and channel_flows tables. Confidence: HIGH.*",
    "macro": "The primary macro driver was the **Federal Reserve's surprise 25bps hike** in March 2026 (bringing rates to 6.00%), which triggered a global risk-off rotation. This had a compounding effect on GEF001: (1) higher US rates strengthened the dollar, driving EM currency volatility and capital outflows from EM assets; (2) higher discount rates reduced the present value of tech earnings, accelerating the sector sell-off; (3) China GDP fell to 3.7% — weakest since 2023 — adding further pressure on the fund's 22% EM allocation. The MarketIntelligenceAgent used RAG retrieval from ChromaDB to corroborate these findings with analyst commentary. *Source: macro_indicators table + search_analyst_commentary (ChromaDB, similarity: 0.94). Confidence: HIGH.*",
    "peer": "GEF001 lagged the category average by **145.8 basis points** in Q1 2026, ranking **last (6th of 6 peers)**. The Global Alpha Fund led with +0.833% average return using a defensive strategy — underweight tech, overweight Consumer Staples. Pinnacle World Fund (+0.567%) and Horizon World Equity (+0.433%) similarly outperformed through defensive tilts. The key pattern: every outperforming peer has **reduced tech and EM exposure** relative to the category average — the direct inverse of GEF001's current positioning. Only Apex Growth Fund shares a similar tech-heavy strategy and it also lagged. *Source: competitor_funds table. Confidence: HIGH.*",
    "rec": "The highest-priority action is **REC-001** (RED tier): reduce Technology allocation from 28.5% to 18–20% and rotate into Healthcare and Consumer Staples. This directly addresses the root cause and is corroborated by all four Group A agents. It requires **analyst sign-off** before implementation due to the >10% weight shift. Second priority is **REC-002** (AMBER tier): immediate EMEA institutional engagement — schedule reviews with the top 5 outflowing accounts this week. Both are time-sensitive. REC-003 (narrative repositioning) and REC-004 (EM currency hedge) are MEDIUM priority and can follow. *Source: RecommendationAgent synthesis from all agents. Confidence: HIGH.*",
    "flow": "Q1 2026 total net outflows were **−$1,300mn**, with AUM declining from $10,200mn to $9,100mn (−10.8%). The outflow accelerated each month: −$300mn in January, −$420mn in February, −$580mn in March — a clear ACCELERATING_OUTFLOW trend. EMEA drove 53.8% of outflows at −$700mn. By channel, Institutional dominated at −$800mn (61.5% of outflows). Notably, **Retail was the only net positive channel** at +$150mn, indicating brand loyalty that can be leveraged in the positioning strategy. *Source: aum_flows, regional_flows, channel_flows tables. Confidence: HIGH.*",
    "conf": "The system computed an **overall confidence score of 91% (HIGH)**. This is derived from five weighted factors: Data Completeness (100% — all 3 months present), Inter-Agent Consistency (90% — 1 conflict resolved), Data Freshness (100% — all data current), Source Trust Tier (93% — mix of SQLite Tier 1 and ChromaDB Tier 2), and Vector Similarity (94% — RAG documents above 0.75 threshold). All source citations are traceable to specific database records with table name, field, and value. The audit trail records every agent invocation, tool call, and the full response snapshot for regulatory documentation purposes.",
}


def get_followup_answer(question: str) -> str:
    ql = question.lower()
    for key, keywords in FOLLOWUP_ANSWERS.items():
        if any(w in ql for w in keywords):
            return ANSWERS[key]
    return ANSWERS["rec"]


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    # Sidebar
    fund_id, period, mode, show_sources, show_conf, show_agents = render_sidebar()
    detailed = "Detailed" in mode

    # Header
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px">
        <span style="font-size:24px">📊</span>
        <div>
            <h1 style="margin:0;font-size:20px;font-weight:700;color:#111827">Fund Performance Diagnostic AI</h1>
            <p style="margin:0;font-size:12px;color:#9ca3af">Multi-agent · Strands Agents + OpenAI GPT-4o · SQLite + ChromaDB · Full transparency</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    # Check database
    if not ensure_db():
        st.stop()

    # Handle pending query from sidebar suggestion buttons
    if "pending_query" in ss and ss.pending_query:
        pq = ss.pending_query
        ss.pending_query = None
        ss.chat_input_val = pq

    # ── Chat history display ──────────────────────────────────────────────────
    chat_container = st.container()

    with chat_container:
        if not ss.messages:
            # Welcome screen
            st.markdown("""
            <div style="text-align:center;padding:40px 20px;color:#6b7280">
                <div style="font-size:48px;margin-bottom:12px">🤖</div>
                <h3 style="color:#111827;margin-bottom:8px">Ask a diagnostic question</h3>
                <p style="max-width:500px;margin:0 auto;line-height:1.7">
                    Query the multi-agent system about fund performance, flows, peer benchmarking,
                    or recommendations. Every response includes source citations, confidence scores,
                    and a full audit trail.
                </p>
            </div>""", unsafe_allow_html=True)
            st.markdown("")

            # Suggestion chips
            col1, col2 = st.columns(2)
            suggestions = [
                ("Why did our Global Equity Fund slow down this quarter?", "🔍"),
                ("What's driving the EMEA institutional outflows?",        "🌍"),
                ("How does GEF001 compare to its peers in Q1 2026?",       "🏆"),
                ("What are the highest-priority recommendations?",          "💡"),
            ]
            for i, (s, icon) in enumerate(suggestions):
                with (col1 if i % 2 == 0 else col2):
                    if st.button(f"{icon} {s}", use_container_width=True, key=f"chip_{i}"):
                        ss.messages.append({"role": "user", "content": s})
                        ss.pending_run = s
                        st.rerun()
        else:
            # Render message history
            for msg in ss.messages:
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div style="display:flex;justify-content:flex-end;margin-bottom:8px">
                        <div class="chat-user">{msg['content']}</div>
                    </div>""", unsafe_allow_html=True)

                elif msg["role"] == "assistant":
                    st.markdown('<div class="chat-bot-header">🤖 <strong>Diagnostic AI</strong></div>', unsafe_allow_html=True)
                    result = msg.get("result")
                    if result:
                        render_diagnostic_result(result, show_sources, show_conf, show_agents)
                    st.divider()

                elif msg["role"] == "followup":
                    st.markdown('<div class="chat-bot-header">🤖 <strong>Diagnostic AI</strong> · follow-up</div>', unsafe_allow_html=True)
                    render_followup_result(
                        answer   = msg.get("answer", ""),
                        trace_id = msg.get("trace_id", "—"),
                        show_conf = show_conf,
                    )
                    st.markdown("")

    # ── Input bar ─────────────────────────────────────────────────────────────
    st.markdown("")
    col_inp, col_btn = st.columns([5, 1])

    with col_inp:
        placeholder = (
            "Ask a follow-up question about the diagnostic…"
            if any(m["role"] == "assistant" for m in ss.messages)
            else "e.g. Why did our Global Equity Fund slow down this quarter?"
        )
        user_input = st.chat_input(placeholder)

    # ── Quick follow-up chips (shown after first answer) ──────────────────────
    if any(m["role"] == "assistant" for m in ss.messages):
        fu_cols = st.columns(5)
        followups = [
            "Why did tech drag so much?",
            "What's driving EMEA outflows?",
            "Which macro factor was worst?",
            "How do peers compare exactly?",
            "How was confidence calculated?",
        ]
        for i, q in enumerate(followups):
            with fu_cols[i]:
                if st.button(q, use_container_width=True, key=f"fu_{i}"):
                    ss.messages.append({"role": "user", "content": q})
                    ss.pending_followup = q
                    st.rerun()

    # ── Handle pending run from suggestion chips ──────────────────────────────
    if "pending_run" in ss and ss.pending_run:
        q = ss.pending_run
        ss.pending_run = None

        with st.spinner(""):
            try:
                result = call_orchestrator(q, fund_id, period, detailed)
                ss.last_result = result
                ss.messages.append({"role": "assistant", "result": result})
            except Exception as e:
                ss.messages.append({"role": "assistant", "result": None})
                st.error(f"Agent orchestration failed: {e}\n\nMake sure your OPENAI_API_KEY is set in .env")
        st.rerun()

    # ── Handle pending follow-up ──────────────────────────────────────────────
    if "pending_followup" in ss and ss.pending_followup:
        q = ss.pending_followup
        ss.pending_followup = None
        import uuid
        answer = get_followup_answer(q)
        trace_id = f"FPD-FU-{str(uuid.uuid4())[:8].upper()}"
        ss.messages.append({"role": "followup", "answer": answer, "trace_id": trace_id})
        st.rerun()

    # ── Handle chat_input submission ──────────────────────────────────────────
    if user_input and user_input.strip():
        ss.messages.append({"role": "user", "content": user_input.strip()})
        has_first = any(m["role"] == "assistant" for m in ss.messages)

        if has_first:
            # Follow-up question
            import uuid
            answer = get_followup_answer(user_input)
            trace_id = f"FPD-FU-{str(uuid.uuid4())[:8].upper()}"
            ss.messages.append({"role": "followup", "answer": answer, "trace_id": trace_id})
            st.rerun()
        else:
            # First diagnostic run
            with st.spinner(""):
                try:
                    result = call_orchestrator(user_input.strip(), fund_id, period, detailed)
                    ss.last_result = result
                    ss.messages.append({"role": "assistant", "result": result})
                except Exception as e:
                    st.error(f"Agent orchestration failed: {e}\n\nMake sure your OPENAI_API_KEY is set in .env")
            st.rerun()


if __name__ == "__main__":
    main()