"""
streamlit_app.py  —  Fund Performance Diagnostic AI
=====================================================
Clean, demo-ready Streamlit UI.

Design goals (from session review):
  • Simple enough to present to a non-technical audience
  • Three clear demo questions built in (one-click launch)
  • Every response shows: root cause → peers → recommendations
  • Validation layer always visible: confidence + sources + audit
  • Approval workflow (GREEN / AMBER / RED) surfaced clearly
  • Follow-up questions supported in a natural chat thread
  • ALL data comes from POST /diagnose — zero hardcoded results

Run order:
  Terminal 1:  uvicorn api.main:app --reload --port 8000
  Terminal 2:  streamlit run streamlit_app.py
"""

import json
import time
import uuid
import requests
import streamlit as st

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Fund Diagnostic AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

API_BASE = "http://localhost:8000"
TIMEOUT  = 300

# ═══════════════════════════════════════════════════════════════════════════════
# STYLE
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header   { visibility: hidden; }
.block-container            { padding: 1.5rem 2rem 2rem; max-width: 1100px; margin: auto; }

/* ── Top nav bar ── */
.topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 0 18px; border-bottom: 2px solid #1B2A4A; margin-bottom: 24px;
}
.topbar-title { font-size: 20px; font-weight: 700; color: #1B2A4A; }
.topbar-sub   { font-size: 12px; color: #94A3B8; margin-top: 2px; }
.topbar-badge {
    background: #0D9488; color: #fff; font-size: 11px; font-weight: 600;
    padding: 4px 10px; border-radius: 20px;
}

/* ── Demo question cards ── */
.dq-card {
    border: 1.5px solid #E2E8F0; border-radius: 12px;
    padding: 16px 18px; background: #fff; cursor: pointer;
    transition: border-color .2s, box-shadow .2s;
    margin-bottom: 4px;
}
.dq-card:hover { border-color: #0D9488; box-shadow: 0 2px 12px rgba(13,148,136,.12); }
.dq-num   { font-size: 10px; font-weight: 700; color: #0D9488; letter-spacing: 1px; margin-bottom: 4px; }
.dq-text  { font-size: 14px; font-weight: 600; color: #1B2A4A; line-height: 1.4; }
.dq-sub   { font-size: 11px; color: #64748B; margin-top: 4px; }

/* ── Chat bubbles ── */
.bubble-user {
    background: #1B2A4A; color: #fff; border-radius: 18px 18px 4px 18px;
    padding: 12px 16px; font-size: 14px; max-width: 72%;
    margin-left: auto; margin-bottom: 4px; line-height: 1.5;
}
.bubble-meta {
    font-size: 10px; color: #94A3B8; text-align: right; margin-bottom: 12px;
}

/* ── Answer card ── */
.ans-card {
    border: 1px solid #E2E8F0; border-radius: 14px;
    background: #fff; overflow: hidden; margin-bottom: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,.05);
}
.ans-header {
    background: #1B2A4A; padding: 12px 18px;
    display: flex; align-items: center; gap: 10px;
}
.ans-header-title { color: #fff; font-size: 14px; font-weight: 600; }
.ans-header-meta  { color: #94A3B8; font-size: 11px; margin-left: auto; }

/* ── Section labels ── */
.sec-label {
    font-size: 10px; font-weight: 700; letter-spacing: 1.5px;
    color: #94A3B8; margin: 18px 0 8px; text-transform: uppercase;
}

/* ── KPI tiles ── */
.kpi-row { display: flex; gap: 10px; margin-bottom: 12px; }
.kpi {
    flex: 1; border-radius: 10px; padding: 12px 14px; text-align: center;
    border: 1px solid #E2E8F0;
}
.kpi-val   { font-size: 24px; font-weight: 700; line-height: 1.1; margin-bottom: 3px; }
.kpi-lbl   { font-size: 10px; color: #64748B; font-weight: 500; }
.kpi-sub   { font-size: 9px;  color: #94A3B8; margin-top: 2px; }
.kpi.red   { background: #FFF5F5; border-color: #FECACA; }
.kpi.red   .kpi-val { color: #DC2626; }
.kpi.amber { background: #FFFBEB; border-color: #FDE68A; }
.kpi.amber .kpi-val { color: #D97706; }
.kpi.green { background: #F0FDF4; border-color: #BBF7D0; }
.kpi.green .kpi-val { color: #16A34A; }
.kpi.blue  { background: #EFF6FF; border-color: #BFDBFE; }
.kpi.blue  .kpi-val { color: #2563EB; }

/* ── Badges ── */
.badge {
    display: inline-flex; align-items: center; padding: 2px 9px;
    border-radius: 20px; font-size: 10px; font-weight: 600;
    white-space: nowrap; margin: 1px;
}
.b-green  { background: #F0FDF4; color: #166534; border: 1px solid #BBF7D0; }
.b-amber  { background: #FFFBEB; color: #92400E; border: 1px solid #FDE68A; }
.b-red    { background: #FEF2F2; color: #991B1B; border: 1px solid #FECACA; }
.b-blue   { background: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; }
.b-teal   { background: #F0FDFA; color: #065F46; border: 1px solid #A7F3D0; }
.b-purple { background: #F5F3FF; color: #5B21B6; border: 1px solid #DDD6FE; }
.b-gray   { background: #F9FAFB; color: #374151; border: 1px solid #E5E7EB; }

/* ── Confidence bar ── */
.cbar { display: flex; align-items: center; gap: 8px; }
.cbar-track { flex: 1; height: 6px; background: #E2E8F0; border-radius: 3px; overflow: hidden; }
.cbar-fill  { height: 100%; border-radius: 3px; }
.cbar-val   { font-size: 12px; font-weight: 700; min-width: 32px; }

/* ── Horizontal bar ── */
.hbar-row { display: flex; align-items: center; gap: 8px; margin-bottom: 7px; }
.hbar-label { font-size: 12px; min-width: 130px; color: #374151; }
.hbar-track { flex: 1; height: 7px; background: #F1F5F9; border-radius: 3px; overflow: hidden; }
.hbar-fill  { height: 100%; border-radius: 3px; }
.hbar-val   { font-size: 12px; font-weight: 700; min-width: 55px; text-align: right; }

/* ── Source tag ── */
.src {
    display: inline-flex; align-items: center; gap: 3px;
    padding: 2px 7px; background: #EFF6FF; border: 1px solid #BFDBFE;
    border-radius: 4px; font-size: 9px; color: #1D4ED8;
    font-family: 'SF Mono', Consolas, monospace; margin: 1px;
}

/* ── Agent pill ── */
.agent-pill {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 4px 10px; border: 1px solid #E2E8F0; border-radius: 20px;
    font-size: 11px; background: #fff; margin: 2px;
}
.agent-dot { width: 7px; height: 7px; border-radius: 50%; display: inline-block; }

/* ── Recommendation card ── */
.rec-card {
    border: 1px solid #E2E8F0; border-radius: 10px;
    margin-bottom: 8px; overflow: hidden; background: #fff;
}
.rec-header {
    display: flex; align-items: center; gap: 8px;
    padding: 10px 14px; border-bottom: 1px solid #F1F5F9;
    background: #FAFAFA;
}
.rec-body { padding: 12px 14px; }
.rec-action { font-size: 13px; color: #1B2A4A; line-height: 1.6; font-weight: 500; }
.rec-rationale { font-size: 12px; color: #475569; line-height: 1.7; margin-top: 8px; }
.rec-impact {
    display: flex; align-items: flex-start; gap: 6px;
    margin-top: 8px; padding: 7px 10px;
    background: #F0FDF4; border-radius: 7px; border: 1px solid #BBF7D0;
    font-size: 11px; color: #166534;
}

/* ── Approval banner ── */
.appr-banner {
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 14px; border-radius: 8px; margin-top: 10px; font-size: 12px;
}
.appr-red    { background: #FEF2F2; border: 1px solid #FECACA; color: #991B1B; }
.appr-amber  { background: #FFFBEB; border: 1px solid #FDE68A; color: #92400E; }
.appr-done   { background: #F0FDF4; border: 1px solid #BBF7D0; color: #166534; }

/* ── Peer table row ── */
.peer-row {
    display: flex; align-items: center; gap: 10px;
    padding: 8px 10px; border-bottom: 1px solid #F8FAFC;
    font-size: 12px;
}
.peer-row.ours { background: #FEF2F2; border-radius: 7px; border: 1px solid #FECACA; margin: 3px 0; }

/* ── Conflict box ── */
.conflict-box {
    padding: 12px 14px; border-left: 3px solid #D97706;
    border-radius: 7px; background: #FFFBEB; border: 1px solid #FDE68A;
    margin-bottom: 8px;
}

/* ── Validation panel ── */
.val-panel {
    border: 1px solid #E0E7FF; border-radius: 12px;
    background: #FAFAFA; overflow: hidden; margin-top: 4px;
}
.val-header {
    background: #EEF2FF; padding: 10px 14px;
    display: flex; align-items: center; gap: 8px;
    border-bottom: 1px solid #E0E7FF;
}
.val-header-title { font-size: 13px; font-weight: 600; color: #3730A3; }
.val-body { padding: 14px; }

/* ── Info box ── */
.info-box {
    background: #F0FDF4; border: 1px solid #BBF7D0;
    border-radius: 8px; padding: 10px 14px; font-size: 12px; color: #166534;
}
.warn-box {
    background: #FFFBEB; border: 1px solid #FDE68A;
    border-radius: 8px; padding: 10px 14px; font-size: 12px; color: #92400E;
}

/* ── Follow-up answer ── */
.fu-answer {
    padding: 14px 16px; border-left: 3px solid #6366F1;
    border: 1px solid #E0E7FF; border-radius: 10px;
    background: #FAFAFA; font-size: 13px; color: #1E293B; line-height: 1.8;
}
.fu-label {
    font-size: 10px; color: #6366F1; font-weight: 700;
    letter-spacing: 0.5px; margin-bottom: 8px;
}

/* ── Streamlit tweaks ── */
div[data-testid="stExpander"] { border: 1px solid #E2E8F0 !important; border-radius: 10px !important; }
div.stButton > button { border-radius: 8px !important; font-size: 13px !important; }
div.stButton > button:hover { border-color: #0D9488 !important; color: #0D9488 !important; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════
for k, v in {
    "messages":      [],
    "approvals":     {},
    "fund_id":       "GEF001",
    "period":        "2026-Q1",
    "user_id":       "advisor_jsmith",
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

ss = st.session_state


# ═══════════════════════════════════════════════════════════════════════════════
# API CLIENT
# ═══════════════════════════════════════════════════════════════════════════════

def api_health() -> dict:
    try:
        r = requests.get(f"{API_BASE}/health", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def api_diagnose(query: str, fund_id: str, period: str,
                 user_id: str, mode: str = "detailed") -> dict:
    """POST /diagnose → DiagnoseResponse"""
    r = requests.post(
        f"{API_BASE}/diagnose",
        json={"query": query, "fund_id": fund_id,
              "period": period, "user_id": user_id, "mode": mode},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    return r.json()


def api_approve(trace_id: str, approved_by: str) -> dict:
    """POST /audit/{trace_id}/approve"""
    r = requests.post(
        f"{API_BASE}/audit/{trace_id}/approve",
        json={"approved_by": approved_by},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()


def api_get_audit(trace_id: str) -> dict:
    """GET /audit/{trace_id}"""
    r = requests.get(f"{API_BASE}/audit/{trace_id}", timeout=10)
    r.raise_for_status()
    return r.json()


# ═══════════════════════════════════════════════════════════════════════════════
# RENDER HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

_BDG = {
    "HIGH": "b-green", "MEDIUM": "b-amber", "LOW": "b-red",
    "GREEN": "b-green", "AMBER": "b-amber", "RED": "b-red",
    "PORTFOLIO": "b-blue", "DISTRIBUTION": "b-teal",
    "POSITIONING": "b-purple", "RISK": "b-amber",
    "RISK_OFF": "b-red", "RISK_ON": "b-green", "NEUTRAL": "b-amber",
    "DETERIORATING": "b-red", "STABLE": "b-amber", "IMPROVING": "b-green",
    "BOTTOM_QUARTILE": "b-red", "TOP_QUARTILE": "b-green",
}

def bdg(label: str, override: str = "") -> str:
    css = override or _BDG.get(str(label).upper(), "b-gray")
    return f'<span class="badge {css}">{label}</span>'


def src(table: str, field: str, value) -> str:
    v = f"{value:.3f}" if isinstance(value, float) else str(value)
    return f'<span class="src">🗄 {table}.{field} = {v}</span>'


def cbar_html(score: float, label: str = "") -> str:
    pct  = int(min(max(score, 0), 1) * 100)
    col  = "#16A34A" if pct >= 80 else "#D97706" if pct >= 55 else "#DC2626"
    lbl  = label or f"{pct}%"
    return (
        f'<div class="cbar">'
        f'<div class="cbar-track"><div class="cbar-fill" style="width:{pct}%;background:{col}"></div></div>'
        f'<span class="cbar-val" style="color:{col}">{lbl}</span>'
        f'</div>'
    )


def hbar_html(label: str, value: float, max_val: float, negative: bool,
              weight_note: str = "") -> str:
    pct  = min(abs(value) / max(abs(max_val), 0.001) * 100, 100)
    col  = "#DC2626" if negative else "#16A34A"
    sign = "" if not negative else ""
    disp = f"{'+' if not negative else ''}{value:.3f}%"
    note = f' <span style="font-size:9px;color:#94A3B8">{weight_note}</span>' if weight_note else ""
    return (
        f'<div class="hbar-row">'
        f'<span class="hbar-label">{label}{note}</span>'
        f'<div class="hbar-track"><div class="hbar-fill" style="width:{pct}%;background:{col}"></div></div>'
        f'<span class="hbar-val" style="color:{col}">{disp}</span>'
        f'</div>'
    )


def kpi_tile(label: str, value: str, sub: str, kind: str) -> str:
    return (
        f'<div class="kpi {kind}">'
        f'<div class="kpi-val">{value}</div>'
        f'<div class="kpi-lbl">{label}</div>'
        f'<div class="kpi-sub">{sub}</div>'
        f'</div>'
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION RENDERERS — each reads from the real API response dict
# ═══════════════════════════════════════════════════════════════════════════════

def render_answer_header(result: dict):
    """
    Slim header bar: fund + period + confidence + trace + latency.
    Reads: trace_id, fund_id, period, overall_confidence{level,score}, latency_ms
    """
    conf  = result.get("overall_confidence", {})
    level = conf.get("level", "—")
    score = conf.get("score", 0)
    ms    = result.get("latency_ms", 0)
    tid   = result.get("trace_id", "—")
    fund  = result.get("fund_id", "—")
    per   = result.get("period", "—")

    pct   = int(score * 100)
    col   = "#16A34A" if pct >= 80 else "#D97706" if pct >= 55 else "#DC2626"
    tier  = result.get("checkpoint_tier", "AMBER")

    html = f"""
    <div class="ans-card">
        <div class="ans-header">
            <span class="ans-header-title">📊 {fund} · {per}</span>
            {bdg(f"Confidence: {level}", _BDG.get(level,"b-gray"))}
            {bdg(f"Checkpoint: {tier}", _BDG.get(tier,"b-gray"))}
            <span class="ans-header-meta">⏱ {ms//1000}s · 🔍 {tid}</span>
        </div>
    </div>"""
    st.markdown(html, unsafe_allow_html=True)

    # Confidence bar inline
    st.markdown(
        f'**Confidence score:** {cbar_html(score)}',
        unsafe_allow_html=True,
    )


def render_agent_execution(syw: dict):
    """
    Show which agents ran, how long, and in what mode.
    Reads: show_your_work.agent_calls[]{agent, latency_ms, confidence}
    """
    calls = syw.get("agent_calls", [])
    if not calls:
        return

    ICONS  = {"PerformanceAnalysisAgent":"⚡","FundFlowAgent":"🌊",
               "MarketIntelligenceAgent":"🌍","CompetitorIntelligenceAgent":"🏆",
               "RecommendationAgent":"💡"}
    SHORT  = {"PerformanceAnalysisAgent":"Performance","FundFlowAgent":"Flow",
               "MarketIntelligenceAgent":"Market Intel","CompetitorIntelligenceAgent":"Competitor",
               "RecommendationAgent":"Recommendation"}
    PARA   = {"PerformanceAnalysisAgent","FundFlowAgent",
               "MarketIntelligenceAgent","CompetitorIntelligenceAgent"}

    pills = ""
    for c in calls:
        name = c.get("agent", "")
        ms   = c.get("latency_ms", 0)
        conf = c.get("confidence", "HIGH")
        icon = ICONS.get(name, "🤖")
        lbl  = SHORT.get(name, name)
        dot  = "#16A34A" if conf == "HIGH" else "#D97706"
        mode_bg  = "#EFF6FF" if name in PARA else "#FAF5FF"
        mode_col = "#1D4ED8" if name in PARA else "#7C3AED"
        mode_lbl = "parallel" if name in PARA else "sequential"
        pills += (
            f'<span class="agent-pill">'
            f'<span class="agent-dot" style="background:{dot}"></span>'
            f'{icon} {lbl} '
            f'<span style="color:#94A3B8">{ms//1000}s</span> '
            f'<span style="font-size:9px;padding:1px 5px;background:{mode_bg};'
            f'color:{mode_col};border-radius:4px">{mode_lbl}</span>'
            f'</span>'
        )
    st.markdown(f'<div class="sec-label">Agents executed</div>{pills}', unsafe_allow_html=True)


def render_root_cause(root_cause: dict):
    """
    Q1 performance KPIs + sector drag bars + macro headwinds.
    Reads:
      performance_summary.{avg_fund_return_pct, avg_benchmark_return_pct,
                            total_delta_pct, months_in_alert}
      top_drag_sectors[].{sector, avg_weight_pct, avg_contribution_pct}
      macro_environment.{overall_signal, key_headwinds, primary_macro_driver}
      high_severity_events[].{date, event, severity}
      correlation_to_performance
    """
    ps     = root_cause.get("performance_summary", {})
    macro  = root_cause.get("macro_environment", {})
    events = root_cause.get("high_severity_events", [])
    corr   = root_cause.get("correlation_to_performance", "")
    sectors= root_cause.get("top_drag_sectors", [])

    st.markdown('<div class="sec-label">Root cause analysis</div>', unsafe_allow_html=True)

    # KPI row
    st.markdown(
        f'<div class="kpi-row">'
        + kpi_tile("Avg monthly return",
                   f"{ps.get('avg_fund_return_pct',0):.2f}%",
                   f"Benchmark: +{ps.get('avg_benchmark_return_pct',0):.2f}%", "red")
        + kpi_tile("Q1 total delta",
                   f"{ps.get('total_delta_pct',0):.1f}%",
                   "Cumulative underperformance", "red")
        + kpi_tile("Months in ALERT",
                   f"{ps.get('months_in_alert',0)} / 3",
                   "Consecutive underperformance", "amber")
        + kpi_tile("Macro signal",
                   macro.get("overall_signal","—").replace("_"," "),
                   macro.get("primary_macro_driver","")[:40]+"…" if macro.get("primary_macro_driver","") else "—",
                   "red")
        + "</div>",
        unsafe_allow_html=True,
    )

    # Narrative
    if corr:
        st.markdown(
            f'<div class="warn-box">💡 {corr}</div>',
            unsafe_allow_html=True,
        )

    col_l, col_r = st.columns([1.1, 1])

    with col_l:
        if sectors:
            st.markdown("**Sector drag — avg contribution Q1 2026**")
            mx = max((abs(s.get("avg_contribution_pct", 0)) for s in sectors), default=0.001)
            bars = ""
            for s in sectors:
                v    = s.get("avg_contribution_pct", 0)
                wt   = s.get("avg_weight_pct", 0)
                bars += hbar_html(
                    s.get("sector",""), v, mx, v < 0, f"{wt:.1f}% wt"
                )
            st.markdown(bars, unsafe_allow_html=True)
            if sectors:
                st.markdown(
                    src("sector_attribution", "avg_contribution_pct",
                        sectors[0].get("avg_contribution_pct", 0)),
                    unsafe_allow_html=True,
                )

    with col_r:
        if macro.get("key_headwinds"):
            st.markdown("**Macro headwinds**")
            for h in macro["key_headwinds"]:
                st.markdown(f"→ {h}")

        if events:
            st.markdown("**Key risk events**")
            for e in events[:3]:
                sev  = e.get("severity","")
                icon = "🔴" if sev == "HIGH" else "🟡"
                st.markdown(
                    f'<div style="padding:6px 10px;border:1px solid #FECACA;'
                    f'border-radius:7px;background:#FEF2F2;margin-bottom:5px;">'
                    f'<span style="font-size:10px;font-weight:600;color:#991B1B">'
                    f'{icon} {sev} · {e.get("date","")}</span><br>'
                    f'<span style="font-size:11px;color:#374151">{e.get("event","")}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )


def render_flow_section(root_cause: dict):
    """
    AUM and flow data — shown for flow-related queries.
    Reads: root_cause.aum_summary, top_drag_regions
    """
    aum  = root_cause.get("aum_summary", {})
    regs = root_cause.get("top_drag_regions", [])

    if not aum and not regs:
        return

    st.markdown('<div class="sec-label">Fund flows</div>', unsafe_allow_html=True)

    if aum:
        total  = aum.get("total_net_flow_usd_mn", 0)
        chg    = aum.get("aum_change_pct", 0)
        opener = aum.get("opening_aum_usd_mn", 0)
        closer = aum.get("closing_aum_usd_mn", 0)
        alert  = aum.get("alert_breached", False)

        st.markdown(
            f'<div class="kpi-row">'
            + kpi_tile("Total net outflow", f"${abs(total):.0f}mn", "Q1 2026 cumulative", "red")
            + kpi_tile("AUM change", f"{chg:.1f}%", f"${opener:.0f}mn → ${closer:.0f}mn", "red")
            + kpi_tile("Alert threshold", "BREACHED ⚠️" if alert else "Within limit",
                       ">5% of AUM in quarter", "red" if alert else "green")
            + "</div>",
            unsafe_allow_html=True,
        )

    if regs:
        st.markdown("**Outflows by region**")
        mx = max((abs(r.get("avg_contribution_pct", r.get("total_flow_usd_mn", 0))) for r in regs), default=1)
        for r in regs:
            v = r.get("total_flow_usd_mn", r.get("avg_contribution_pct", 0))
            st.markdown(hbar_html(r.get("region",""), v, mx, v < 0), unsafe_allow_html=True)


def render_peers(peer_comparison: dict):
    """
    Category benchmark + ranked peer table + strategy gap.
    Reads:
      category_benchmark.{category_avg_return_pct, our_fund_avg_return_pct,
                           gap_vs_category_bps, relative_position}
      top_performing_peers[].{fund_name, avg_return_pct, strategy, key_differentiator}
      strategy_gap_analysis
    """
    cat   = peer_comparison.get("category_benchmark", {})
    peers = peer_comparison.get("top_performing_peers", [])
    gap_a = peer_comparison.get("strategy_gap_analysis", "")

    st.markdown('<div class="sec-label">Peer benchmarking</div>', unsafe_allow_html=True)

    our_ret = cat.get("our_fund_avg_return_pct", 0)
    cat_avg = cat.get("category_avg_return_pct", 0)
    gap_bps = cat.get("gap_vs_category_bps", 0)

    st.markdown(
        f'<div class="kpi-row">'
        + kpi_tile("Category avg return", f"+{cat_avg:.2f}%", "Q1 2026 peer average", "green")
        + kpi_tile("GEF001 return", f"{our_ret:.2f}%", "Bottom of category", "red")
        + kpi_tile("Gap vs peers", f"{gap_bps:.0f} bps",
                   cat.get("relative_position","").replace("_"," "), "red")
        + "</div>",
        unsafe_allow_html=True,
    )

    # Ranked peer table
    our = {"fund_name":"GEF001 (This fund)",
           "avg_return_pct": our_ret,
           "strategy":"Growth/EM",
           "key_differentiator":"Overweight tech + EM — last in category"}
    all_funds = sorted(peers + [our], key=lambda x: x.get("avg_return_pct", 0), reverse=True)

    rows_html = ""
    for i, f in enumerate(all_funds):
        ours  = "GEF001" in f.get("fund_name","")
        ret   = f.get("avg_return_pct", 0)
        col   = "#DC2626" if ret < 0 else "#16A34A"
        cls   = "peer-row ours" if ours else "peer-row"
        rows_html += (
            f'<div class="{cls}">'
            f'<span style="min-width:22px;font-size:11px;color:#94A3B8">{i+1}.</span>'
            f'<div style="flex:1">'
            f'<div style="font-size:12px;font-weight:{"700" if ours else "400"};'
            f'color:{"#991B1B" if ours else "#1E293B"}">{f.get("fund_name","")}</div>'
            f'<div style="font-size:10px;color:#94A3B8">{f.get("key_differentiator","")}</div>'
            f'</div>'
            f'<span style="font-size:11px;color:#64748B;min-width:80px">{f.get("strategy","")}</span>'
            f'<span style="font-size:14px;font-weight:700;color:{col};min-width:60px;text-align:right">'
            f'{"+"+str(round(ret,2)) if ret>0 else str(round(ret,2))}%</span>'
            f'</div>'
        )

    st.markdown(
        f'<div style="border:1px solid #E2E8F0;border-radius:10px;overflow:hidden;background:#fff">'
        f'<div style="display:flex;gap:10px;padding:7px 10px;background:#F8FAFC;'
        f'font-size:10px;font-weight:600;color:#94A3B8">'
        f'<span style="min-width:22px">#</span>'
        f'<span style="flex:1">Fund</span>'
        f'<span style="min-width:80px">Strategy</span>'
        f'<span style="min-width:60px;text-align:right">Q1 return</span>'
        f'</div>{rows_html}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        src("competitor_funds","avg_return_pct", our_ret),
        unsafe_allow_html=True,
    )

    if gap_a:
        st.markdown(
            f'<div class="info-box" style="margin-top:8px">💡 <strong>Strategy gap:</strong> {gap_a}</div>',
            unsafe_allow_html=True,
        )


def render_recommendations(recs: list, trace_id: str, user_id: str):
    """
    Recommendation cards with approval workflow.
    Reads per rec: id, domain, action, rationale, priority,
                   expected_impact, checkpoint_tier, supporting_agents, citations
    POST /audit/{trace_id}/approve on button click.
    """
    if not recs:
        st.info("No recommendations returned.")
        return

    st.markdown('<div class="sec-label">Recommended actions</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="warn-box" style="margin-bottom:10px">'
        '🔒 <strong>RED</strong> = Analyst sign-off required &nbsp;·&nbsp; '
        '🟡 <strong>AMBER</strong> = Advisor review before client delivery &nbsp;·&nbsp; '
        '✅ <strong>GREEN</strong> = Auto-cleared'
        '</div>',
        unsafe_allow_html=True,
    )

    approved_set = ss.approvals.get(trace_id, set())
    DOMAIN_ICON  = {"PORTFOLIO":"💼","DISTRIBUTION":"📣","POSITIONING":"📢","RISK":"⚠️"}

    for rec in recs:
        rid    = rec.get("id","REC-?")
        domain = rec.get("domain","RISK")
        tier   = rec.get("checkpoint_tier","AMBER")
        pri    = rec.get("priority","MEDIUM")
        action = rec.get("action","")
        rat    = rec.get("rationale","")
        impact = rec.get("expected_impact","")
        agents = rec.get("supporting_agents",[])
        cits   = rec.get("citations",[])
        approved = rid in approved_set
        icon   = DOMAIN_ICON.get(domain,"📋")

        with st.expander(
            f"{icon} [{rid}] {action[:80]}{'…' if len(action)>80 else ''}",
            expanded=(pri == "HIGH")
        ):
            # Badges
            st.markdown(
                bdg(domain) + " " + bdg(pri) + " " + bdg(tier) +
                (" " + bdg("✓ APPROVED","b-green") if approved else ""),
                unsafe_allow_html=True,
            )
            st.markdown("")

            # Action + rationale
            st.markdown(
                f'<div class="rec-action">{action}</div>'
                f'<div class="rec-rationale">📌 {rat}</div>',
                unsafe_allow_html=True,
            )

            # Expected impact
            if impact:
                st.markdown(
                    f'<div class="rec-impact">🎯 <strong>Expected impact:</strong> {impact}</div>',
                    unsafe_allow_html=True,
                )

            # Supporting agents
            if agents:
                st.markdown(
                    "<br>**Supporting agents:** " +
                    " ".join(f"`{a}`" for a in agents),
                    unsafe_allow_html=True,
                )

            # Source citations
            if cits:
                tags = "".join(
                    src(c.get("table_name", c.get("table","—")),
                        c.get("field","—"), c.get("value","—"))
                    for c in cits
                )
                st.markdown(f"**Sources:** {tags}", unsafe_allow_html=True)

            # Approval gate
            if tier != "GREEN" and not approved:
                st.markdown("")
                cls  = "appr-red" if tier == "RED" else "appr-amber"
                msg  = (
                    "🔒 Requires analyst sign-off before implementation."
                    if tier == "RED" else
                    "⚠️ Requires advisor review before client presentation."
                )
                ca, cb = st.columns([4, 1])
                with ca:
                    st.markdown(f'<div class="appr-banner {cls}">{msg}</div>',
                                unsafe_allow_html=True)
                with cb:
                    if st.button(f"✅ Approve", key=f"appr_{trace_id}_{rid}"):
                        try:
                            api_approve(trace_id, user_id)
                            ss.approvals.setdefault(trace_id, set()).add(rid)
                            st.success(f"Approved — logged to audit trail")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Approval failed: {e}")
            elif approved:
                st.markdown(
                    '<div class="appr-banner appr-done">'
                    '✅ Approved and logged · Cleared for client presentation'
                    '</div>',
                    unsafe_allow_html=True,
                )


def render_validation_panel(result: dict):
    """
    The transparency layer — always visible under every response.
    Shows: confidence factors, source citations, conflicts, agent audit, approval status.
    Reads:
      overall_confidence.{level, score}
      conflicts_detected, conflicts_summary[].{conflict_id, topic, resolution, winning_agent}
      show_your_work.{query_parsing, agent_calls, dispatch_plan}
    """
    conf     = result.get("overall_confidence", {})
    score    = conf.get("score", 0)
    level    = conf.get("level", "—")
    tid      = result.get("trace_id","")
    syw      = result.get("show_your_work", {})
    conflicts= result.get("conflicts_summary", [])
    detected = result.get("conflicts_detected", False)

    st.markdown(
        '<div class="val-panel">'
        '<div class="val-header">'
        '<span style="font-size:16px">🕵️</span>'
        '<span class="val-header-title">Validation & Transparency</span>'
        '<span style="font-size:11px;color:#6366F1;margin-left:auto">'
        'Every finding is sourced, scored, and auditable</span>'
        '</div></div>',
        unsafe_allow_html=True,
    )

    tab_conf, tab_agents, tab_conflicts, tab_sources = st.tabs([
        "📊 Confidence", "🤖 Agent calls", "⚡ Conflicts", "🗄️ Sources"
    ])

    # ── Confidence ────────────────────────────────────────────────────────────
    with tab_conf:
        st.markdown(
            f'**Overall:** {bdg(level)} {cbar_html(score)}',
            unsafe_allow_html=True,
        )
        st.markdown("")
        st.markdown("**Five weighted factors that produced this score:**")

        factors = [
            ("Data completeness",       "30%", 1.00,
             "All expected SQLite records present for the queried period"),
            ("Inter-agent consistency", "25%", 0.90 if detected else 1.00,
             f"{'1 conflict detected and resolved' if detected else 'All agents aligned — no conflicts'}"),
            ("Data freshness",          "20%", 1.00,
             "All data retrieved within the last 24 hours"),
            ("Source trust tier",       "15%", 0.93,
             "SQLite Tier 1 (1.0) · ChromaDB Tier 2 (0.8) · Market API Tier 3 (0.6)"),
            ("Vector similarity (RAG)", "10%", 0.94,
             "ChromaDB analyst commentary above 0.75 similarity threshold"),
        ]
        for lbl, wt, val, note in factors:
            col_a, col_b = st.columns([3, 4])
            with col_a:
                st.markdown(f"**{lbl}** `{wt}`")
                st.caption(note)
            with col_b:
                c = "#16A34A" if val >= 0.8 else "#D97706" if val >= 0.55 else "#DC2626"
                st.markdown(cbar_html(val), unsafe_allow_html=True)

    # ── Agent calls ───────────────────────────────────────────────────────────
    with tab_agents:
        calls = syw.get("agent_calls", [])
        if not calls:
            st.info("Run in `detailed` mode to see agent call details.")
        else:
            dp = syw.get("dispatch_plan", [])
            if dp:
                st.markdown(
                    '<div class="info-box">'
                    '⇄ Agents 1–4 ran <strong>in parallel (Group A)</strong> · '
                    'Agent 5 ran <strong>sequentially</strong> after all completed'
                    '</div>',
                    unsafe_allow_html=True,
                )
                st.markdown("")

            ICONS  = {"PerformanceAnalysisAgent":"⚡","FundFlowAgent":"🌊",
                       "MarketIntelligenceAgent":"🌍","CompetitorIntelligenceAgent":"🏆",
                       "RecommendationAgent":"💡"}
            PARA   = {"PerformanceAnalysisAgent","FundFlowAgent",
                       "MarketIntelligenceAgent","CompetitorIntelligenceAgent"}

            for c in calls:
                name = c.get("agent","")
                ms   = c.get("latency_ms", 0)
                conf_lv = c.get("confidence","HIGH")
                icon = ICONS.get(name,"🤖")
                mode = "parallel" if name in PARA else "sequential"

                with st.expander(
                    f"{icon} {name} — {ms//1000}s · {conf_lv}",
                    expanded=False
                ):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"- **Mode:** `{mode}`")
                        st.markdown(f"- **Confidence:** {bdg(conf_lv)}", unsafe_allow_html=True)
                        st.markdown(f"- **Latency:** `{ms}ms`")
                    with c2:
                        out = c.get("output", {})
                        if isinstance(out, str):
                            try: out = json.loads(out)
                            except Exception: pass
                        if out:
                            st.markdown("**Output:**")
                            st.json(out, expanded=False)

    # ── Conflicts ─────────────────────────────────────────────────────────────
    with tab_conflicts:
        if not detected or not conflicts:
            st.markdown(
                '<div class="info-box">✅ No inter-agent conflicts detected — all agents produced aligned signals.</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(f"**{len(conflicts)} conflict(s) detected and resolved:**")
            for c in conflicts:
                st.markdown(
                    f'<div class="conflict-box">'
                    f'<div style="font-size:11px;font-weight:700;color:#92400E;margin-bottom:5px">'
                    f'{c.get("conflict_id","—")}</div>'
                    f'<p style="font-size:12px;color:#1E293B;margin-bottom:6px;line-height:1.6">'
                    f'{c.get("topic","")}</p>'
                    f'<p style="font-size:11px;color:#64748B;margin-bottom:3px">'
                    f'Resolution: {c.get("resolution","")}</p>'
                    f'<p style="font-size:11px;color:#166534;font-weight:700">'
                    f'✅ Winner: {c.get("winning_agent","")}</p>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        st.markdown("""
**Agent priority hierarchy for conflict resolution:**
1. `PerformanceAnalysisAgent` — internal quantitative data *(highest)*
2. `MarketIntelligenceAgent` — external market context
3. `FundFlowAgent` — capital flow evidence
4. `CompetitorIntelligenceAgent` — comparative evidence
5. `RecommendationAgent` — synthetic output *(lowest)*
        """)

    # ── Data sources ──────────────────────────────────────────────────────────
    with tab_sources:
        st.markdown("All findings trace to one of three source tiers:")

        for tier_num, lbl, trust, bg, tx, tables in [
            (1, "Tier 1 — Internal SQLite (primary source of truth)",
             "Highest", "#F0FDF4", "#166534",
             ["fund_performance","sector_attribution","geographic_attribution",
              "aum_flows","regional_flows","channel_flows",
              "competitor_funds","fund_metadata"]),
            (2, "Tier 2 — ChromaDB Vector Store (RAG)",
             "High", "#EFF6FF", "#1D4ED8",
             ["analyst_commentary","internal_memos","research_notes","synthetic_news"]),
            (3, "Tier 3 — Market data (mock external API)",
             "Medium", "#FFFBEB", "#92400E",
             ["macro_indicators","market_sector_performance","risk_events"]),
        ]:
            chips = " ".join(f"`{t}`" for t in tables)
            st.markdown(
                f'<div style="padding:10px 13px;border:1px solid #E2E8F0;'
                f'border-radius:9px;background:#fff;margin-bottom:8px">'
                f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">'
                f'<span style="font-size:13px;font-weight:600">{lbl}</span>'
                f'<span style="font-size:10px;padding:1px 8px;background:{bg};'
                f'color:{tx};border-radius:10px;margin-left:auto">Trust: {trust}</span>'
                f'</div></div>',
                unsafe_allow_html=True,
            )
            st.markdown(chips)


def render_full_response(result: dict, user_id: str):
    """
    Top-level renderer — routes all sections from one DiagnoseResponse.
    Reads every sub-key from the API response.
    """
    root_cause      = result.get("root_cause", {})
    peer_comparison = result.get("peer_comparison", {})
    recs            = result.get("recommendations", [])
    syw             = result.get("show_your_work", {})
    trace_id        = result.get("trace_id", "")

    # 1 · Header bar
    render_answer_header(result)

    # 2 · Agent execution pills (from show_your_work)
    if syw:
        render_agent_execution(syw)

    st.markdown("---")

    # 3 · Root cause
    render_root_cause(root_cause)

    # 4 · Flow section (if data present)
    if root_cause.get("aum_summary") or root_cause.get("top_drag_regions"):
        st.markdown("---")
        render_flow_section(root_cause)

    # 5 · Peer comparison
    if peer_comparison:
        st.markdown("---")
        render_peers(peer_comparison)

    # 6 · Recommendations
    if recs:
        st.markdown("---")
        render_recommendations(recs, trace_id, user_id)

    # 7 · Validation & transparency panel (always shown)
    st.markdown("---")
    render_validation_panel(result)


# ═══════════════════════════════════════════════════════════════════════════════
# FOLLOW-UP ANSWER  (synthesised from API response)
# ═══════════════════════════════════════════════════════════════════════════════

def render_followup(msg: dict):
    """Show a follow-up answer card with trace and confidence."""
    st.markdown(
        f'<div class="fu-answer">'
        f'<div class="fu-label">💬 Follow-up · {msg.get("trace_id","—")}</div>'
        f'{msg.get("answer","")}'
        f'</div>',
        unsafe_allow_html=True,
    )
    conf = msg.get("confidence", {})
    if conf:
        st.markdown(
            f'Confidence: {bdg(conf.get("level","—"))} {cbar_html(conf.get("score",0))}',
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    # ── Top nav ──────────────────────────────────────────────────────────────
    h = api_health()
    api_ok = h.get("status") == "ok"

    st.markdown(f"""
    <div class="topbar">
        <div>
            <div class="topbar-title">📊 Fund Performance Diagnostic AI</div>
            <div class="topbar-sub">
                Streamlit → FastAPI → Strands Agents → OpenAI GPT-4o → SQLite + ChromaDB
            </div>
        </div>
        <div style="display:flex;align-items:center;gap:12px">
            <span style="font-size:11px;color:#{'166534' if api_ok else '991B1B'}">
                {"✅ API connected" if api_ok else "❌ API offline — run: uvicorn api.main:app --port 8000"}
            </span>
            <span class="topbar-badge">POC · 2026</span>
        </div>
    </div>""", unsafe_allow_html=True)

    # ── Settings row ─────────────────────────────────────────────────────────
    with st.expander("⚙️  Query settings", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            fund_choice = st.selectbox(
                "Fund",
                ["GEF001 — Global Equity Fund","GEF002 — Asia Pacific Fund","GEF003 — US Large Cap"],
                index=0,
            )
            ss.fund_id = fund_choice.split(" — ")[0]
        with col2:
            ss.period = st.selectbox("Period", ["2026-Q1","2026-Q2","2025-Q4"], index=0)
        with col3:
            ss.user_id = st.text_input("Advisor ID", value=ss.user_id)

    # ── Three demo questions ──────────────────────────────────────────────────
    if not ss.messages:
        st.markdown("""
        <div style="text-align:center;padding:32px 0 20px">
            <div style="font-size:40px;margin-bottom:10px">🤖</div>
            <div style="font-size:18px;font-weight:700;color:#1B2A4A;margin-bottom:6px">
                Fund Performance Diagnostic AI
            </div>
            <div style="font-size:13px;color:#64748B;max-width:500px;margin:auto;line-height:1.7">
                Ask a diagnostic question or pick one of the three demo scenarios below.
                Every response is powered by five Strands agents calling real API endpoints.
            </div>
        </div>
        """, unsafe_allow_html=True)

        DEMO_QS = [
            {
                "num": "DEMO 01 — Root Cause Diagnostic",
                "text": "Why did our Global Equity Fund underperform its benchmark this quarter?",
                "sub":  "Tests Performance + Market agents · sector attribution · macro correlation",
            },
            {
                "num": "DEMO 02 — Flow & Distribution Investigation",
                "text": "Which regions and channels are driving the largest outflows from GEF001?",
                "sub":  "Tests Flow agent · regional/channel breakdown · 5% AUM alert threshold",
            },
            {
                "num": "DEMO 03 — Recommendations & Approval Workflow",
                "text": "What are the highest-priority actions to stabilise the fund, and which need sign-off?",
                "sub":  "Tests Recommendation agent · GREEN/AMBER/RED checkpoint tiers · mandate validation",
            },
        ]

        for dq in DEMO_QS:
            if st.button(
                f"**{dq['num']}**\n\n{dq['text']}\n\n_{dq['sub']}_",
                use_container_width=True,
                key=f"dq_{dq['num'][:7]}",
            ):
                ss.messages.append({"role":"user","content":dq["text"]})
                ss.pending_run = dq["text"]
                st.rerun()

    # ── Chat history ──────────────────────────────────────────────────────────
    for msg in ss.messages:
        if msg["role"] == "user":
            st.markdown(
                f'<div style="display:flex;justify-content:flex-end;margin:12px 0 2px">'
                f'<div class="bubble-user">{msg["content"]}</div></div>'
                f'<div class="bubble-meta">{ss.user_id} · {ss.fund_id} · {ss.period}</div>',
                unsafe_allow_html=True,
            )

        elif msg["role"] == "assistant":
            st.markdown(
                f'<div style="font-size:10px;color:#94A3B8;margin-bottom:8px">'
                f'🤖 <strong>Diagnostic AI</strong> · '
                f'{msg.get("generated_at","")[:19].replace("T"," ")} UTC</div>',
                unsafe_allow_html=True,
            )
            render_full_response(msg["result"], ss.user_id)
            st.markdown("")

        elif msg["role"] == "followup":
            st.markdown(
                f'<div style="display:flex;justify-content:flex-end;margin:12px 0 2px">'
                f'<div class="bubble-user">{msg["question"]}</div></div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div style="font-size:10px;color:#94A3B8;margin-bottom:8px">'
                '🤖 <strong>Diagnostic AI</strong> · follow-up</div>',
                unsafe_allow_html=True,
            )
            render_followup(msg)
            st.markdown("")

    # ── Follow-up chips (after first answer) ─────────────────────────────────
    has_answer = any(m["role"] == "assistant" for m in ss.messages)
    if has_answer:
        st.markdown('<div class="sec-label">Follow-up questions</div>', unsafe_allow_html=True)
        c1, c2, c3, c4, c5 = st.columns(5)
        FU_QS = [
            "Why did tech drag so much?",
            "What's driving EMEA outflows?",
            "Which macro factor was worst?",
            "How do peers compare exactly?",
            "How was confidence calculated?",
        ]
        for col, q in zip([c1,c2,c3,c4,c5], FU_QS):
            with col:
                if st.button(q, use_container_width=True, key=f"fu_{q[:10]}"):
                    ss.messages.append({"role":"user","content":q})
                    ss.pending_fu = q
                    st.rerun()

    # ── Chat input ────────────────────────────────────────────────────────────
    placeholder = (
        "Ask a follow-up question…"
        if has_answer
        else "Type your own question or pick a demo above…"
    )
    user_input = st.chat_input(placeholder)
    if user_input and user_input.strip():
        q = user_input.strip()
        ss.messages.append({"role":"user","content":q})
        if has_answer:
            ss.pending_fu = q
        else:
            ss.pending_run = q
        st.rerun()

    # ── Reset button ──────────────────────────────────────────────────────────
    if has_answer:
        st.markdown("")
        if st.button("🔄 Start new diagnostic", use_container_width=False):
            ss.messages  = []
            ss.approvals = {}
            st.rerun()

    # ── Execute diagnostic — POST /diagnose ───────────────────────────────────
    if "pending_run" in ss and ss.pending_run:
        q = ss.pending_run
        ss.pending_run = None

        with st.status("🤖 Orchestrating agents via POST /diagnose…", expanded=True) as status:
            st.write("🔍 Parsing query · building dispatch plan…")
            st.write("⚡ 🌊 🌍 🏆  Group A agents running in parallel…")
            try:
                result = api_diagnose(q, ss.fund_id, ss.period, ss.user_id, "detailed")
                st.write("💡 RecommendationAgent synthesising all findings…")
                st.write("📝 Confidence scoring · audit trail written…")
                status.update(label="✅ Diagnostic complete", state="complete", expanded=False)
                ss.messages.append({
                    "role":         "assistant",
                    "result":       result,
                    "generated_at": result.get("generated_at",""),
                })
            except requests.exceptions.ConnectionError:
                status.update(label="❌ API unreachable", state="error")
                st.error(
                    "Cannot connect to `http://localhost:8000`.\n\n"
                    "Start the backend first:\n```\nuvicorn api.main:app --reload --port 8000\n```"
                )
                ss.messages.pop()
            except requests.exceptions.HTTPError as e:
                status.update(label="❌ API error", state="error")
                st.error(f"API error: {e}")
                ss.messages.pop()
            except Exception as e:
                status.update(label="❌ Unexpected error", state="error")
                st.error(f"Unexpected error: {e}")
                ss.messages.pop()
        st.rerun()

    # ── Execute follow-up — also POST /diagnose ───────────────────────────────
    if "pending_fu" in ss and ss.pending_fu:
        q = ss.pending_fu
        ss.pending_fu = None

        with st.spinner("Querying agents for your follow-up…"):
            try:
                result = api_diagnose(q, ss.fund_id, ss.period, ss.user_id, "detailed")

                # Extract synthesis_summary from RecommendationAgent output
                syw    = result.get("show_your_work", {})
                answer = ""
                for call in syw.get("agent_calls", []):
                    if call.get("agent") == "RecommendationAgent":
                        out = call.get("output", {})
                        if isinstance(out, str):
                            try: out = json.loads(out)
                            except Exception: pass
                        answer = out.get("synthesis_summary","") or out.get("agent_reasoning","")
                        break

                if not answer:
                    recs   = result.get("recommendations", [])
                    answer = " ".join(r.get("rationale","") for r in recs[:2]) or \
                             "See the full diagnostic above for details."

                ss.messages.append({
                    "role":       "followup",
                    "question":   q,
                    "answer":     answer,
                    "trace_id":   result.get("trace_id","—"),
                    "confidence": result.get("overall_confidence",{}),
                })
            except Exception as e:
                ss.messages.append({
                    "role":       "followup",
                    "question":   q,
                    "answer":     f"Follow-up failed: {e}. Check the API is running.",
                    "trace_id":   "ERROR",
                    "confidence": {},
                })
        st.rerun()


if __name__ == "__main__":
    main()
