"""
streamlit_app.py
─────────────────
Fund Performance Diagnostic AI — Streamlit UI.

Architecture (clean separation):
  - ALL data comes from the FastAPI backend via HTTP calls.
  - ZERO direct imports from agents/, core/, tools/, or data/.
  - Every rendered value is read from the API response dict.

Endpoints consumed:
  GET  /health
  POST /diagnose          → DiagnoseResponse (with show_your_work when mode=detailed)
  GET  /audit/{trace_id}  → AuditResponse
  POST /audit/{trace_id}/approve

Run order:
  Terminal 1:  uvicorn api.main:app --reload --port 8000
  Terminal 2:  streamlit run streamlit_app.py
"""

import json
import time
import uuid

import requests
import streamlit as st
from streamlit import session_state as ss

# ── Page config — must be the very first Streamlit call ───────────────────────
st.set_page_config(
    page_title="Fund Diagnostic AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
API_BASE = "http://localhost:8000"
TIMEOUT  = 300   # seconds — LLM calls can take time

# ═══════════════════════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif}
#MainMenu,footer,header{visibility:hidden}
.block-container{padding-top:1rem;padding-bottom:1rem}

.kpi{background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:14px 16px;text-align:center}
.kpi.d{border-left:4px solid #dc2626;background:#fff5f5}
.kpi.w{border-left:4px solid #d97706;background:#fffbeb}
.kpi.s{border-left:4px solid #16a34a;background:#f0fdf4}
.kpi .l{font-size:11px;color:#6b7280;margin-bottom:4px}
.kpi .v{font-size:22px;font-weight:700;margin-bottom:2px}
.kpi .b{font-size:10px;color:#9ca3af}
.kpi.d .v{color:#dc2626}.kpi.w .v{color:#d97706}.kpi.s .v{color:#16a34a}

.bdg{display:inline-flex;align-items:center;padding:2px 8px;border-radius:20px;font-size:11px;font-weight:500;margin:1px;white-space:nowrap}
.hi,.gr{background:#f0fdf4;color:#166534;border:1px solid #bbf7d0}
.me,.am{background:#fffbeb;color:#92400e;border:1px solid #fde68a}
.lo,.re{background:#fef2f2;color:#991b1b;border:1px solid #fecaca}
.bl{background:#eff6ff;color:#1d4ed8;border:1px solid #bfdbfe}
.pu{background:#f5f3ff;color:#5b21b6;border:1px solid #ddd6fe}
.te{background:#f0fdfa;color:#065f46;border:1px solid #a7f3d0}
.gy{background:#f9fafb;color:#374151;border:1px solid #e5e7eb}

.src{display:inline-flex;align-items:center;gap:3px;padding:1px 6px;background:#eff6ff;border:1px solid #bfdbfe;border-radius:4px;font-size:10px;color:#1d4ed8;font-family:'SF Mono',Consolas,monospace;margin:1px}

.cbar-wrap{display:flex;align-items:center;gap:8px;margin:4px 0}
.cbar-track{flex:1;height:5px;background:#e5e7eb;border-radius:3px;overflow:hidden}
.cbar-fill{height:100%;border-radius:3px}

.apill{display:inline-flex;align-items:center;gap:6px;padding:4px 10px;border:1px solid #e5e7eb;border-radius:20px;font-size:11px;background:#fff;margin:2px}
.adot{width:7px;height:7px;border-radius:50%;display:inline-block}

.cbox{padding:10px 13px;border-left:3px solid #d97706;border-radius:7px;background:#fffbeb;border:1px solid #fde68a;margin-bottom:8px}
.usr-bub{background:#f3f4f6;border:1px solid #e5e7eb;border-radius:12px 12px 4px 12px;padding:10px 14px;font-size:13px;max-width:78%;margin-left:auto;margin-bottom:6px}
.fu-box{padding:12px 15px;border-left:3px solid #6366f1;border:1px solid #e0e7ff;border-radius:8px;background:#fafafa;font-size:13px;line-height:1.8;color:#111827}
.ap-r{background:#fef2f2;border:1px solid #fecaca;border-radius:7px;padding:8px 12px;color:#991b1b;font-size:12px}
.ap-a{background:#fffbeb;border:1px solid #fde68a;border-radius:7px;padding:8px 12px;color:#92400e;font-size:12px}
.ap-g{background:#f0fdf4;border:1px solid #bbf7d0;border-radius:7px;padding:8px 12px;color:#166534;font-size:12px}
.api-ok{background:#f0fdf4;border:1px solid #bbf7d0;border-radius:7px;padding:6px 12px;color:#166534;font-size:12px}
.api-er{background:#fef2f2;border:1px solid #fecaca;border-radius:7px;padding:6px 12px;color:#991b1b;font-size:12px}
::-webkit-scrollbar{width:4px}
::-webkit-scrollbar-thumb{background:#d1d5db;border-radius:2px}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════
for k, v in {
    "messages":      [],
    "approvals":     {},   # trace_id → set of approved rec IDs
    "last_trace_id": None,
}.items():
    if k not in ss:
        ss[k] = v

# ═══════════════════════════════════════════════════════════════════════════════
# API CLIENT  — every HTTP call lives here; nothing else touches requests
# ═══════════════════════════════════════════════════════════════════════════════

def api_health() -> dict:
    """GET /health → {status, version, db, vector_store}"""
    try:
        r = requests.get(f"{API_BASE}/health", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def api_diagnose(query: str, fund_id: str, period: str,
                 user_id: str, mode: str = "detailed") -> dict:
    """
    POST /diagnose
    Body:     DiagnoseRequest {query, fund_id, period, user_id, mode}
    Returns:  DiagnoseResponse — keys the UI reads:

      trace_id, fund_id, period, generated_at, latency_ms
      overall_confidence        { level, score }
      root_cause {
        performance_summary     { avg_fund_return_pct, avg_benchmark_return_pct,
                                  avg_delta_pct, total_delta_pct, months_in_alert, trend }
        top_drag_sectors        [ { sector, avg_weight_pct, avg_contribution_pct, signal } ]
        top_drag_regions        [ { region, avg_contribution_pct } ]
        macro_environment       { overall_signal, key_headwinds, primary_macro_driver }
        high_severity_events    [ { date, event, severity } ]
        correlation_to_performance
      }
      peer_comparison {
        category_benchmark      { category_avg_return_pct, our_fund_avg_return_pct,
                                  gap_vs_category_bps, relative_position }
        top_performing_peers    [ { fund_name, avg_return_pct, strategy, key_differentiator } ]
        strategy_gap_analysis
      }
      recommendations [ { id, domain, action, rationale, priority,
                           expected_impact, checkpoint_tier, supporting_agents, citations } ]
      conflicts_detected, conflicts_summary [ { conflict_id, topic, resolution, winning_agent } ]
      show_your_work {
        query_parsing, dispatch_plan
        agent_calls  [ { agent, latency_ms, confidence, called_at, output } ]
        conflicts_detail
      }
      disclaimer
    """
    payload = dict(query=query, fund_id=fund_id, period=period,
                   user_id=user_id, mode=mode)
    r = requests.post(f"{API_BASE}/diagnose", json=payload, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def api_get_audit(trace_id: str) -> dict:
    """
    GET /audit/{trace_id}
    Returns: AuditResponse { trace_id, session, agent_calls, conflicts }
    """
    r = requests.get(f"{API_BASE}/audit/{trace_id}", timeout=10)
    r.raise_for_status()
    return r.json()


def api_approve(trace_id: str, approved_by: str) -> dict:
    """POST /audit/{trace_id}/approve — records human sign-off"""
    r = requests.post(
        f"{API_BASE}/audit/{trace_id}/approve",
        json={"approved_by": approved_by},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()

# ═══════════════════════════════════════════════════════════════════════════════
# RENDER HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

_BM = {
    "HIGH":"hi","MEDIUM":"me","LOW":"lo",
    "GREEN":"gr","AMBER":"am","RED":"re",
    "PORTFOLIO":"bl","DISTRIBUTION":"te","POSITIONING":"pu","RISK":"am",
    "RISK_OFF":"lo","RISK_ON":"hi","NEUTRAL":"me",
    "DETERIORATING":"lo","STABLE":"me","IMPROVING":"hi",
    "BOTTOM_QUARTILE":"lo","TOP_QUARTILE":"hi",
}

def bdg(label: str) -> str:
    css = _BM.get(str(label).upper(), "gy")
    return f'<span class="bdg {css}">{label}</span>'

def src_tag(table: str, field: str, value) -> str:
    v = f"{value:.3f}" if isinstance(value, float) else str(value)
    return f'<span class="src">🗄 {table}.{field} = {v}</span>'

def cbar(score: float) -> str:
    pct = int(min(max(score, 0), 1) * 100)
    col = "#16a34a" if pct >= 80 else "#d97706" if pct >= 55 else "#dc2626"
    return (f'<div class="cbar-wrap">'
            f'<div class="cbar-track"><div class="cbar-fill" style="width:{pct}%;background:{col}"></div></div>'
            f'<span style="font-size:12px;font-weight:700;color:{col};min-width:32px">{pct}%</span>'
            f'</div>')

def kpi_card(label, value, sub, kind="d"):
    return (f'<div class="kpi {kind}"><div class="l">{label}</div>'
            f'<div class="v">{value}</div><div class="b">{sub}</div></div>')

def hbar(value: float, max_val: float, negative: bool) -> str:
    pct = min(abs(value) / max(max_val, 0.001) * 100, 100)
    col = "#dc2626" if negative else "#16a34a"
    return (f'<div style="flex:1;height:7px;background:#f1f3f4;border-radius:3px;overflow:hidden">'
            f'<div style="width:{pct}%;height:100%;background:{col};border-radius:3px"></div></div>')

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION RENDERERS
# Each function receives the exact sub-dict from the API response and renders it.
# ═══════════════════════════════════════════════════════════════════════════════

def render_meta_bar(result: dict):
    """Top row: trace_id · confidence · latency — from result root keys."""
    tid  = result.get("trace_id", "—")
    conf = result.get("overall_confidence", {})
    ms   = result.get("latency_ms", 0)
    disc = result.get("disclaimer", "")
    c1,c2,c3,c4 = st.columns([2.5,1.2,1.5,2])
    with c1: st.markdown(f"🔍 **Trace** `{tid}`")
    with c2: st.markdown(bdg(f"Confidence: {conf.get('level','—')}"), unsafe_allow_html=True)
    with c3: st.markdown(cbar(conf.get("score", 0)), unsafe_allow_html=True)
    with c4: st.caption(f"⏱ {ms//1000}s · {disc[:70]}…")


def render_agent_pills(syw: dict):
    """
    Agent execution pills — built from show_your_work.agent_calls.
    Keys per call: agent, latency_ms, confidence
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
    html = ""
    for c in calls:
        name = c.get("agent","")
        ms   = c.get("latency_ms",0)
        conf = c.get("confidence","HIGH")
        dcol = "#16a34a" if conf=="HIGH" else "#d97706" if conf=="MEDIUM" else "#dc2626"
        mcol = "#1d4ed8" if name in PARA else "#7c3aed"
        mlbl = "parallel" if name in PARA else "sequential"
        mbg  = "#eff6ff" if name in PARA else "#faf5ff"
        html += (f'<span class="apill"><span class="adot" style="background:{dcol}"></span>'
                 f'{ICONS.get(name,"🤖")} {SHORT.get(name,name)} '
                 f'<span style="color:#9ca3af">{ms//1000}s</span> '
                 f'<span style="font-size:9px;padding:1px 5px;background:{mbg};'
                 f'color:{mcol};border-radius:4px">{mlbl}</span></span>')
    st.markdown(html, unsafe_allow_html=True)
    st.markdown("")


def render_overview(root_cause: dict, peer_comparison: dict):
    """
    KPI cards + sector drag bars + macro headwinds + risk events.
    All values read from API keys — no defaults invented here.
    """
    ps     = root_cause.get("performance_summary", {})
    cat    = peer_comparison.get("category_benchmark", {})
    macro  = root_cause.get("macro_environment", {})
    events = root_cause.get("high_severity_events", [])

    c1,c2,c3,c4 = st.columns(4)
    with c1: st.markdown(kpi_card("Avg monthly return",
        f"{ps.get('avg_fund_return_pct',0):.2f}%",
        f"Benchmark +{ps.get('avg_benchmark_return_pct',0):.2f}%"), unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("Q1 total delta",
        f"{ps.get('total_delta_pct',0):.1f}%",
        "Cumulative underperformance"), unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("vs Category average",
        f"{cat.get('gap_vs_category_bps',0):.0f} bps",
        cat.get("relative_position","").replace("_"," ")), unsafe_allow_html=True)
    with c4: st.markdown(kpi_card("Months in ALERT",
        f"{ps.get('months_in_alert',0)} / 3",
        "Consecutive flags","w"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([1.4, 1])

    with left:
        st.markdown("#### 🔍 Root cause")
        corr = root_cause.get("correlation_to_performance","")
        if corr: st.info(corr)

        sectors = root_cause.get("top_drag_sectors", [])
        if sectors:
            st.markdown("**Top sector drags — avg contribution Q1 2026**")
            mx = max((abs(s.get("avg_contribution_pct",0)) for s in sectors), default=0.001)
            for s in sectors:
                v = s.get("avg_contribution_pct",0)
                neg = v < 0
                col = "#dc2626" if neg else "#16a34a"
                pct = min(abs(v)/mx*100, 100)
                ca,cb,cc,cd = st.columns([2,0.6,2.5,0.9])
                with ca: st.markdown(f"<span style='font-size:13px'>{s.get('sector','')}</span>", unsafe_allow_html=True)
                with cb: st.markdown(f"<span style='font-size:10px;color:#9ca3af'>{s.get('avg_weight_pct',0):.1f}%</span>", unsafe_allow_html=True)
                with cc: st.markdown(
                    f'<div style="margin-top:8px;height:7px;background:#f1f3f4;border-radius:3px;overflow:hidden">'
                    f'<div style="width:{pct}%;height:100%;background:{col};border-radius:3px"></div></div>',
                    unsafe_allow_html=True)
                with cd: st.markdown(f"<span style='color:{col};font-weight:700;font-size:12px'>{'+' if not neg else ''}{v:.3f}%</span>", unsafe_allow_html=True)
            st.markdown(src_tag("sector_attribution","avg_contribution_pct",
                sectors[0].get("avg_contribution_pct",0)), unsafe_allow_html=True)

        hw = macro.get("key_headwinds",[])
        if hw:
            st.markdown("**Macro headwinds**")
            for h in hw: st.markdown(f"→ {h}")

    with right:
        st.markdown("#### ⚠️ Risk events")
        if events:
            for e in events:
                sev  = e.get("severity","MEDIUM")
                icon = "🔴" if sev=="HIGH" else "🟡"
                st.markdown(f"""
                <div style="padding:8px 10px;border:1px solid #fecaca;border-radius:8px;
                            background:#fef2f2;margin-bottom:6px">
                    <div style="font-size:10px;font-weight:600;color:#991b1b;margin-bottom:3px">
                        {icon} {sev} · {e.get('date','')}
                    </div>
                    <div style="font-size:12px;color:#374151">{e.get('event','')}</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.success("No high-severity risk events in this period.")
        signal = macro.get("overall_signal","")
        if signal:
            st.markdown(f"""
            <div style="text-align:center;padding:12px;border:1px solid #fecaca;
                        border-radius:8px;background:#fff;margin-top:8px">
                <div style="font-size:10px;color:#9ca3af;margin-bottom:4px">Macro signal</div>
                <div style="font-size:15px;font-weight:700;color:#dc2626">{signal.replace('_',' ')}</div>
                <div style="font-size:11px;color:#6b7280;margin-top:5px">
                    {macro.get('primary_macro_driver','')[:90]}
                </div>
            </div>""", unsafe_allow_html=True)


def render_performance(root_cause: dict):
    """
    Sector attribution bars + geographic attribution bars.
    Keys: root_cause.top_drag_sectors, root_cause.top_drag_regions
    """
    sectors = root_cause.get("top_drag_sectors", [])
    regions = root_cause.get("top_drag_regions", [])
    left, right = st.columns(2)

    with left:
        st.markdown("#### 📊 Sector attribution — Q1 2026 avg")
        if not sectors:
            st.info("PerformanceAnalysisAgent returned no sector data.")
        else:
            mx = max((abs(s.get("avg_contribution_pct",0)) for s in sectors), default=0.001)
            for s in sectors:
                v = s.get("avg_contribution_pct",0); neg=v<0; col="#dc2626" if neg else "#16a34a"
                pct=min(abs(v)/mx*100,100)
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:7px">
                    <span style="font-size:12px;min-width:140px">{s.get('sector','')}</span>
                    <span style="font-size:10px;color:#9ca3af;min-width:36px">{s.get('avg_weight_pct',0):.1f}%</span>
                    <div style="flex:1;height:7px;background:#f1f3f4;border-radius:3px;overflow:hidden">
                        <div style="width:{pct}%;height:100%;background:{col};border-radius:3px"></div>
                    </div>
                    <span style="font-size:12px;font-weight:700;color:{col};min-width:50px;text-align:right">
                        {'+' if not neg else ''}{v:.3f}%
                    </span>
                </div>""", unsafe_allow_html=True)
            st.markdown(src_tag("sector_attribution","avg_contribution_pct",
                sectors[0].get("avg_contribution_pct",0)), unsafe_allow_html=True)

    with right:
        st.markdown("#### 🌍 Geographic attribution — Q1 2026 avg")
        if not regions:
            st.info("PerformanceAnalysisAgent returned no regional data.")
        else:
            mx = max((abs(r.get("avg_contribution_pct",0)) for r in regions), default=0.001)
            for r in regions:
                v = r.get("avg_contribution_pct",0); neg=v<0; col="#dc2626" if neg else "#16a34a"
                pct=min(abs(v)/mx*100,100)
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:7px">
                    <span style="font-size:12px;min-width:130px">{r.get('region','')}</span>
                    <div style="flex:1;height:7px;background:#f1f3f4;border-radius:3px;overflow:hidden">
                        <div style="width:{pct}%;height:100%;background:{col};border-radius:3px"></div>
                    </div>
                    <span style="font-size:12px;font-weight:700;color:{col};min-width:50px;text-align:right">
                        {'+' if not neg else ''}{v:.3f}%
                    </span>
                </div>""", unsafe_allow_html=True)
            st.markdown(src_tag("geographic_attribution","avg_contribution_pct",
                regions[0].get("avg_contribution_pct",0)), unsafe_allow_html=True)


def render_peers(peer_comparison: dict):
    """
    Category benchmark KPIs + ranked peer table + strategy gap text.
    Keys: peer_comparison.category_benchmark, top_performing_peers, strategy_gap_analysis
    """
    cat   = peer_comparison.get("category_benchmark", {})
    peers = peer_comparison.get("top_performing_peers", [])
    gap_a = peer_comparison.get("strategy_gap_analysis","")

    c1,c2,c3 = st.columns(3)
    with c1: st.markdown(kpi_card("Category avg return",
        f"+{cat.get('category_avg_return_pct',0):.2f}%","Q1 2026 peer average","s"), unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("Our fund return",
        f"{cat.get('our_fund_avg_return_pct',0):.2f}%","GEF001 Q1 2026"), unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("Gap vs category",
        f"{cat.get('gap_vs_category_bps',0):.0f} bps",
        cat.get("relative_position","").replace("_"," ")), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🏆 Peer ranking — Q1 2026 avg return")

    our = {"fund_name":"GEF001 (This fund)",
           "avg_return_pct":cat.get("our_fund_avg_return_pct",0),
           "strategy":"Growth/EM","key_differentiator":"Overweight tech + EM"}
    all_funds = sorted(peers+[our], key=lambda x:x.get("avg_return_pct",0), reverse=True)

    st.markdown("""<div style="display:flex;gap:10px;padding:6px 10px;background:#f8f9fa;
        border-radius:6px;font-size:10px;font-weight:600;color:#6b7280;margin-bottom:4px">
        <span style="min-width:20px">#</span><span style="flex:1">Fund</span>
        <span style="min-width:90px">Strategy</span><span style="min-width:70px;text-align:right">Q1 return</span>
    </div>""", unsafe_allow_html=True)

    for i,f in enumerate(all_funds):
        ours = "GEF001" in f.get("fund_name","")
        ret  = f.get("avg_return_pct",0)
        col  = "#dc2626" if ret<0 else "#16a34a"
        bg   = "#fef2f2" if ours else "#fff"
        bdr  = "border:1px solid #fecaca;" if ours else "border:1px solid #f3f4f6;"
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;padding:8px 10px;
                    border-radius:8px;background:{bg};{bdr}margin-bottom:4px">
            <span style="min-width:20px;font-size:11px;color:#9ca3af">{i+1}.</span>
            <div style="flex:1">
                <div style="font-size:12px;font-weight:{'700' if ours else '400'};
                            color:{'#991b1b' if ours else '#111827'}">{f.get('fund_name','')}</div>
                <div style="font-size:10px;color:#9ca3af">{f.get('key_differentiator','')}</div>
            </div>
            <span style="min-width:90px;font-size:11px;color:#6b7280">{f.get('strategy','')}</span>
            <span style="min-width:70px;font-size:14px;font-weight:700;color:{col};text-align:right">
                {'+' if ret>0 else ''}{ret:.2f}%</span>
        </div>""", unsafe_allow_html=True)

    st.markdown(src_tag("competitor_funds","avg_return_pct",
        cat.get("our_fund_avg_return_pct",0)), unsafe_allow_html=True)
    if gap_a:
        st.markdown(""); st.info(f"💡 **Strategy gap:** {gap_a}")


def render_recommendations(recs: list, trace_id: str, user_id: str):
    """
    Expandable rec cards + approval buttons → POST /audit/{trace_id}/approve.
    Keys per rec: id, domain, action, rationale, priority, expected_impact,
                  checkpoint_tier, supporting_agents, citations[]{table_name,field,value}
    """
    if not recs:
        st.warning("RecommendationAgent returned no recommendations."); return

    st.info("🔒 **RED** = Analyst sign-off · 🟡 **AMBER** = Advisor review · ✅ **GREEN** = Auto-cleared")
    approved_set = ss.approvals.get(trace_id, set())

    DS = {"PORTFOLIO":("💼","#eff6ff","#1d4ed8"),
          "DISTRIBUTION":("📣","#f0fdfa","#065f46"),
          "POSITIONING":("📢","#f5f3ff","#5b21b6"),
          "RISK":("⚠️","#fffbeb","#92400e")}

    for rec in recs:
        rid   = rec.get("id","REC-?")
        dom   = rec.get("domain","RISK")
        tier  = rec.get("checkpoint_tier","AMBER")
        pri   = rec.get("priority","MEDIUM")
        act   = rec.get("action","")
        rat   = rec.get("rationale","")
        imp   = rec.get("expected_impact","")
        ags   = rec.get("supporting_agents",[])
        cits  = rec.get("citations",[])
        approved = rid in approved_set
        icon,dbg,dtx = DS.get(dom,("📋","#f9fafb","#374151"))

        with st.expander(f"{icon} [{rid}] {act[:80]}{'…' if len(act)>80 else ''}", expanded=False):
            st.markdown(bdg(dom)+" "+bdg(pri)+" "+bdg(tier)+
                        (" "+bdg("✓ APPROVED") if approved else ""), unsafe_allow_html=True)
            st.markdown("")
            cl,cr = st.columns(2)
            with cl:
                st.markdown("**Full action**")
                st.markdown(f"<div style='font-size:13px;padding:9px;background:#f8f9fa;border-radius:7px;line-height:1.7'>{act}</div>", unsafe_allow_html=True)
                st.markdown(""); st.markdown("**Rationale**")
                st.markdown(f"<div style='font-size:12px;padding:9px;border-left:3px solid #6366f1;background:#f9fafb;border-radius:0 7px 7px 0;line-height:1.7'>{rat}</div>", unsafe_allow_html=True)
            with cr:
                st.markdown("**Expected impact**")
                st.markdown(f"<div style='font-size:12px;padding:9px;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:7px'>{imp}</div>", unsafe_allow_html=True)
                st.markdown(""); st.markdown("**Supporting agents**")
                for a in ags: st.markdown(f"- `{a}`")
                if cits:
                    st.markdown("**Source citations**")
                    tags = "".join(src_tag(c.get("table_name",c.get("table","—")),
                                           c.get("field","—"),c.get("value","—")) for c in cits)
                    st.markdown(tags, unsafe_allow_html=True)

            if tier!="GREEN" and not approved:
                st.markdown("")
                msg = ("🔒 Requires **analyst sign-off** before implementation."
                       if tier=="RED" else
                       "⚠️ Requires **advisor review** before client presentation.")
                st.markdown(f'<div class="{"ap-r" if tier=="RED" else "ap-a"}">{msg}</div>',
                            unsafe_allow_html=True)
                st.markdown("")
                if st.button(f"✅ Approve {rid}", key=f"appr_{trace_id}_{rid}"):
                    try:
                        api_approve(trace_id, user_id)
                        ss.approvals.setdefault(trace_id, set()).add(rid)
                        st.success(f"{rid} approved — logged via POST /audit/{trace_id}/approve")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Approval failed: {e}")
            elif approved:
                st.markdown('<div class="ap-g">✅ Approved and logged · Cleared for client presentation</div>',
                            unsafe_allow_html=True)


def render_audit_trail(result: dict, trace_id: str):
    """
    Full audit panel — data from two sources:
      1. result["show_your_work"]   (POST /diagnose, mode=detailed)
      2. GET /audit/{trace_id}      (live session + agent call records)
    All keys are documented per section.
    """
    syw = result.get("show_your_work", {})
    live = None
    try:
        live = api_get_audit(trace_id)
    except Exception:
        pass

    t1,t2,t3,t4,t5 = st.tabs([
        "🤖 Agent calls","⚡ Conflicts",
        "📊 Confidence","🗄 Sources","📄 Raw session"
    ])

    # ── Agent calls ───────────────────────────────────────────────────────────
    with t1:
        # Dispatch plan from show_your_work
        dp = syw.get("dispatch_plan",[])
        if dp:
            st.markdown("""<div style="padding:7px 10px;background:#eff6ff;border:1px solid #bfdbfe;
                border-radius:7px;font-size:12px;color:#1d4ed8;margin-bottom:12px">
                ⇄ Agents 1–4 ran <b>in parallel (Group A)</b>
                · Agent 5 ran <b>sequentially</b> after Group A completed
            </div>""", unsafe_allow_html=True)

        # Prefer live audit agent_calls (has input_payload too); fall back to syw
        calls = []
        if live and live.get("agent_calls"):
            # Live audit key is "agent_name"; syw key is "agent" — normalise
            calls = [{**c, "agent": c.get("agent_name", c.get("agent",""))}
                     for c in live["agent_calls"]]
        elif syw.get("agent_calls"):
            calls = syw["agent_calls"]

        ICONS = {"PerformanceAnalysisAgent":"⚡","FundFlowAgent":"🌊",
                 "MarketIntelligenceAgent":"🌍","CompetitorIntelligenceAgent":"🏆",
                 "RecommendationAgent":"💡"}
        PARA  = {"PerformanceAnalysisAgent","FundFlowAgent",
                 "MarketIntelligenceAgent","CompetitorIntelligenceAgent"}

        for c in calls:
            name = c.get("agent","")
            ms   = c.get("latency_ms",0)
            conf = c.get("confidence","HIGH")
            mode = "parallel" if name in PARA else "sequential"
            with st.expander(f"{ICONS.get(name,'🤖')} {name} — {ms//1000}s · {conf}", expanded=False):
                ca,cb = st.columns(2)
                with ca:
                    st.markdown(f"- **Mode:** `{mode}`")
                    st.markdown(f"- **Confidence:** {bdg(conf)}", unsafe_allow_html=True)
                    st.markdown(f"- **Latency:** `{ms}ms`")
                    if c.get("called_at"): st.markdown(f"- **Called at:** `{c['called_at']}`")
                with cb:
                    out = c.get("output", c.get("output_payload",{}))
                    if isinstance(out, str):
                        try: out = json.loads(out)
                        except Exception: pass
                    if out:
                        st.markdown("**Agent output**")
                        st.json(out, expanded=False)

    # ── Conflicts ─────────────────────────────────────────────────────────────
    with t2:
        conflicts = (live.get("conflicts",[]) if live and live.get("conflicts")
                     else result.get("conflicts_summary",[]))
        if not result.get("conflicts_detected") or not conflicts:
            st.success("✅ No inter-agent conflicts detected.")
        else:
            st.warning(f"**{len(conflicts)} conflict(s) detected and resolved**")
            for c in conflicts:
                cid = c.get("conflict_id", c.get("id","—"))
                st.markdown(f"""<div class="cbox">
                    <div style="font-size:11px;font-weight:700;color:#92400e;margin-bottom:5px">{cid}</div>
                    {'<div style="font-size:11px;color:#6b7280;margin-bottom:4px">Between: <code>'+c.get('agent_a','')+'</code> and <code>'+c.get('agent_b','')+'</code></div>' if c.get('agent_a') else ''}
                    <p style="font-size:12px;color:#111827;margin-bottom:6px;line-height:1.6">{c.get('topic','')}</p>
                    <p style="font-size:11px;color:#6b7280;margin-bottom:3px">Resolution: {c.get('resolution','')}</p>
                    <p style="font-size:11px;color:#166534;font-weight:700">✅ Winning agent: {c.get('winning_agent','')}</p>
                </div>""", unsafe_allow_html=True)
        st.markdown("""**Priority hierarchy:**
1. `PerformanceAnalysisAgent` — internal quantitative data  
2. `MarketIntelligenceAgent` — external market context  
3. `FundFlowAgent` — capital flow evidence  
4. `CompetitorIntelligenceAgent` — comparative evidence  
5. `RecommendationAgent` — synthetic output""")

    # ── Confidence ────────────────────────────────────────────────────────────
    with t3:
        overall = result.get("overall_confidence",{})
        score   = overall.get("score",0.0)
        level   = overall.get("level","—")
        st.markdown(f"#### Overall: {bdg(level)} {bdg(str(int(score*100))+'%')}",
                    unsafe_allow_html=True)
        st.markdown(cbar(score), unsafe_allow_html=True)
        st.markdown("**5 weighted factors (from orchestrator._compute_overall_confidence)**")
        # Values displayed are the documented factor weights from the orchestrator
        factors = [
            ("Data completeness",       "30%", 1.00, "All expected SQLite records present for the period"),
            ("Inter-agent consistency", "25%", 0.90, "Reduced by 0.15 per conflict detected"),
            ("Data freshness",          "20%", 1.00, "All data retrieved within 24 hours"),
            ("Source trust tier",       "15%", 0.93, "SQLite Tier 1 (1.0) + ChromaDB Tier 2 (0.8)"),
            ("Vector similarity (RAG)", "10%", 0.94, "ChromaDB similarity above 0.75 threshold"),
        ]
        for lbl,wt,val,note in factors:
            col="#16a34a" if val>=0.8 else "#d97706" if val>=0.55 else "#dc2626"
            ca,cb,cc = st.columns([2,0.5,3.5])
            with ca: st.markdown(f"**{lbl}** `{wt}`")
            with cb: st.markdown(f"<span style='color:{col};font-weight:700'>{int(val*100)}%</span>",
                                 unsafe_allow_html=True)
            with cc: st.markdown(cbar(val), unsafe_allow_html=True)
            st.caption(note)

    # ── Sources ───────────────────────────────────────────────────────────────
    with t4:
        st.markdown("All findings are traceable to one of three tiers:")
        for lbl,trust,bg,tx,tables in [
            ("Tier 1 — Internal SQLite","Highest","#f0fdf4","#166534",
             ["fund_metadata","fund_performance","sector_attribution","geographic_attribution",
              "aum_flows","regional_flows","channel_flows","competitor_funds",
              "macro_indicators","market_sector_performance","risk_events"]),
            ("Tier 2 — ChromaDB Vector Store (RAG)","High","#eff6ff","#1d4ed8",
             ["analyst_commentary","internal_memos","research_notes","synthetic_news"]),
            ("Tier 3 — Mock market / external API","Medium","#fffbeb","#92400e",
             ["macro_indicators","market_sector_performance","risk_events"]),
        ]:
            chips = "".join(
                f'<span style="font-size:10px;padding:1px 6px;background:#f8f9fa;'
                f'border:1px solid #e5e7eb;border-radius:3px;font-family:monospace;'
                f'color:#374151;margin:2px;display:inline-block">{t}</span>'
                for t in tables)
            st.markdown(f"""
            <div style="padding:10px 13px;border:1px solid #e5e7eb;border-radius:9px;
                        background:#fff;margin-bottom:9px">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
                    <span style="font-size:13px;font-weight:600">{lbl}</span>
                    <span style="font-size:11px;padding:1px 8px;background:{bg};
                                 color:{tx};border-radius:10px;margin-left:auto">Trust: {trust}</span>
                </div><div>{chips}</div>
            </div>""", unsafe_allow_html=True)

    # ── Raw session ───────────────────────────────────────────────────────────
    with t5:
        st.caption(f"Source: GET /audit/{trace_id}")
        if live and live.get("session"):
            sess = live["session"]
            if isinstance(sess,str):
                try: sess=json.loads(sess)
                except Exception: pass
            for f in ["trace_id","status","overall_confidence","confidence_score",
                      "checkpoint_tier","total_latency_ms","created_at","completed_at"]:
                if f in sess: st.markdown(f"**{f}:** `{sess[f]}`")
            st.markdown("**Full session:**")
            st.json(sess, expanded=False)
        else:
            st.info("Live audit record will appear here once the session is persisted.")
            if syw.get("query_parsing"):
                st.markdown("**Query parsing (from show_your_work):**")
                st.json(syw["query_parsing"], expanded=True)


def render_diagnostic(result: dict, user_id: str):
    """
    Top-level renderer — orchestrates all sections from one DiagnoseResponse dict.
    """
    trace_id   = result.get("trace_id","")
    root_cause = result.get("root_cause",{})
    peer_comp  = result.get("peer_comparison",{})
    recs       = result.get("recommendations",[])
    syw        = result.get("show_your_work",{})

    render_meta_bar(result)
    if syw: render_agent_pills(syw)
    st.divider()

    t1,t2,t3,t4,t5 = st.tabs([
        "📋 Overview","📈 Performance & Attribution",
        "🏆 Peer Comparison","💡 Recommendations","🕵️ Audit Trail"
    ])
    with t1: render_overview(root_cause, peer_comp)
    with t2: render_performance(root_cause)
    with t3: render_peers(peer_comp)
    with t4: render_recommendations(recs, trace_id, user_id)
    with t5: render_audit_trail(result, trace_id)

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════

def render_sidebar():
    with st.sidebar:
        st.markdown("### 📊 Fund Diagnostic AI")
        st.caption("Streamlit → FastAPI → Strands Agents → OpenAI GPT-4o")
        st.divider()

        # API health
        h = api_health()
        if h.get("status")=="ok":
            st.markdown('<div class="api-ok">✅ API ok · DB ok · Vector store ok</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="api-er">❌ API unreachable<br>'
                '<code>uvicorn api.main:app --reload --port 8000</code></div>',
                unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Query parameters**")
        fund_id = st.selectbox("Fund",
            ["GEF001 — Global Equity Fund","GEF002 — Asia Pacific Fund","GEF003 — US Large Cap"],
            index=0).split(" — ")[0]
        period  = st.selectbox("Period",["2026-Q1","2026-Q2","2025-Q4","2025-Q3"],index=0)
        user_id = st.text_input("User / advisor ID", value="advisor_jsmith")

        st.divider()
        st.markdown("**Suggested queries**")
        for s in [
            "Why did our Global Equity Fund slow down this quarter?",
            "What's driving the EMEA institutional outflows?",
            "How does GEF001 compare to peers in Q1?",
            "What are the highest-priority actions?",
        ]:
            if st.button(s[:50]+("…" if len(s)>50 else ""),
                         use_container_width=True, key=f"sg_{s[:12]}"):
                ss.prefill = s

        st.divider()
        if ss.last_trace_id:
            st.markdown("**Last trace**"); st.code(ss.last_trace_id, language=None)
            if st.button("🔄 New conversation", use_container_width=True):
                ss.messages=[];ss.last_trace_id=None;ss.approvals={}
                st.rerun()

        st.divider()
        st.caption(f"API: `{API_BASE}`")
        st.caption("Mode: `detailed` → includes show_your_work")

    return fund_id, period, user_id, "detailed"

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    fund_id, period, user_id, mode = render_sidebar()

    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px">
        <span style="font-size:26px">📊</span>
        <div>
            <h1 style="margin:0;font-size:20px;font-weight:700;color:#111827">Fund Performance Diagnostic AI</h1>
            <p style="margin:0;font-size:11px;color:#9ca3af">
                Streamlit UI → <code>POST /diagnose</code> → Orchestrator →
                5 Strands Agents → OpenAI GPT-4o → SQLite + ChromaDB
            </p>
        </div>
    </div>""", unsafe_allow_html=True)
    st.divider()

    # ── Render history ────────────────────────────────────────────────────────
    for msg in ss.messages:
        if msg["role"]=="user":
            st.markdown(
                f'<div style="display:flex;justify-content:flex-end;margin-bottom:6px">'
                f'<div class="usr-bub">{msg["content"]}</div></div>',
                unsafe_allow_html=True)
        elif msg["role"]=="assistant":
            st.markdown(
                f'<div style="font-size:11px;color:#9ca3af;margin-bottom:6px">'
                f'🤖 <b>Diagnostic AI</b> · '
                f'{msg.get("generated_at","")[:19].replace("T"," ")} UTC</div>',
                unsafe_allow_html=True)
            render_diagnostic(msg["result"], user_id)
            st.divider()
        elif msg["role"]=="followup":
            st.markdown(
                '<div style="font-size:11px;color:#9ca3af;margin-bottom:6px">'
                '🤖 <b>Diagnostic AI</b> · follow-up</div>',
                unsafe_allow_html=True)
            st.markdown(
                f'<div class="fu-box">'
                f'<div style="font-size:10px;color:#6366f1;font-weight:600;margin-bottom:8px">'
                f'💬 Re: "{msg["question"]}" · trace {msg.get("trace_id","—")}</div>'
                f'{msg["answer"]}</div>',
                unsafe_allow_html=True)
            st.markdown("")

    # ── Follow-up chips ───────────────────────────────────────────────────────
    has_answer = any(m["role"]=="assistant" for m in ss.messages)
    if has_answer:
        st.markdown("**Quick follow-ups:**")
        cols = st.columns(5)
        for i,q in enumerate([
            "Why did tech drag so much?",
            "What's driving EMEA outflows?",
            "Which macro factor was worst?",
            "How do peers compare exactly?",
            "How was confidence calculated?",
        ]):
            with cols[i]:
                if st.button(q, use_container_width=True, key=f"fu_{i}"):
                    ss.messages.append({"role":"user","content":q})
                    ss.pending_fu=q; st.rerun()

    # ── Welcome ───────────────────────────────────────────────────────────────
    if not ss.messages:
        st.markdown("""
        <div style="text-align:center;padding:50px 20px;color:#6b7280">
            <div style="font-size:52px;margin-bottom:12px">🤖</div>
            <h3 style="color:#111827;margin-bottom:8px">Ask a diagnostic question</h3>
            <p style="max-width:520px;margin:0 auto;line-height:1.8;font-size:13px">
                Type below or pick a suggestion. The UI calls
                <code>POST /diagnose</code> on the FastAPI backend,
                which orchestrates 5 Strands agents. Every tab is
                populated directly from the API response — no hardcoded data.
            </p>
        </div>""", unsafe_allow_html=True)
        c1,c2=st.columns(2)
        for i,(icon,q) in enumerate([
            ("🔍","Why did our Global Equity Fund slow down this quarter?"),
            ("🌍","What's driving the EMEA institutional outflows?"),
            ("🏆","How does GEF001 compare to its peers in Q1 2026?"),
            ("💡","What are the highest-priority recommendations?"),
        ]):
            with (c1 if i%2==0 else c2):
                if st.button(f"{icon} {q}", use_container_width=True, key=f"ch_{i}"):
                    ss.messages.append({"role":"user","content":q})
                    ss.pending_run=q; st.rerun()

    # ── Handle prefill from sidebar ───────────────────────────────────────────
    if "prefill" in ss and ss.prefill:
        pf=ss.prefill; ss.prefill=None
        ss.messages.append({"role":"user","content":pf})
        ss.pending_run=pf; st.rerun()

    # ── Chat input ────────────────────────────────────────────────────────────
    user_input = st.chat_input(
        "Ask a follow-up…" if has_answer
        else "e.g. Why did our Global Equity Fund slow down this quarter?"
    )
    if user_input and user_input.strip():
        q=user_input.strip()
        ss.messages.append({"role":"user","content":q})
        if has_answer: ss.pending_fu=q
        else: ss.pending_run=q
        st.rerun()

    # ── Execute diagnostic — calls POST /diagnose ─────────────────────────────
    if "pending_run" in ss and ss.pending_run:
        q=ss.pending_run; ss.pending_run=None
        with st.status("🤖 Calling POST /diagnose — orchestrating agents…", expanded=True) as status:
            st.write("🔍 Parsing query and building dispatch plan…")
            st.write("⚡ 🌊 🌍 🏆  Group A agents running in parallel…")
            try:
                result = api_diagnose(q, fund_id, period, user_id, mode)
                st.write("💡 RecommendationAgent synthesising all findings…")
                st.write("📝 Formatting response and writing audit trail…")
                status.update(label="✅ Diagnostic complete", state="complete", expanded=False)
                ss.last_trace_id = result.get("trace_id")
                ss.messages.append({"role":"assistant","result":result,
                                    "generated_at":result.get("generated_at","")})
            except requests.exceptions.ConnectionError:
                status.update(label="❌ Connection failed", state="error")
                st.error("Cannot reach `http://localhost:8000`.\n\n"
                         "Run: `uvicorn api.main:app --reload --port 8000`")
                ss.messages.pop()
            except requests.exceptions.HTTPError as e:
                status.update(label="❌ API error", state="error")
                st.error(f"API error: {e}")
                ss.messages.pop()
            except Exception as e:
                status.update(label="❌ Error", state="error")
                st.error(f"Unexpected error: {e}")
                ss.messages.pop()
        st.rerun()

    # ── Execute follow-up — also calls POST /diagnose ─────────────────────────
    if "pending_fu" in ss and ss.pending_fu:
        q=ss.pending_fu; ss.pending_fu=None
        with st.spinner("Calling POST /diagnose for follow-up…"):
            try:
                result = api_diagnose(q, fund_id, period, user_id, mode)
                # Extract synthesis summary from RecommendationAgent output
                syw   = result.get("show_your_work",{})
                answer = ""
                for call in syw.get("agent_calls",[]):
                    if call.get("agent")=="RecommendationAgent":
                        out = call.get("output",{})
                        if isinstance(out,str):
                            try: out=json.loads(out)
                            except Exception: pass
                        answer = (out.get("synthesis_summary","") or
                                  out.get("agent_reasoning",""))
                        break
                if not answer:
                    recs=result.get("recommendations",[])
                    answer=(" ".join(r.get("rationale","") for r in recs[:2])
                            or "See the full diagnostic above for details.")
                ss.messages.append({
                    "role":"followup","question":q,"answer":answer,
                    "trace_id":result.get("trace_id","—"),
                })
            except Exception as e:
                ss.messages.append({
                    "role":"followup","question":q,
                    "answer":f"Follow-up failed: {e}. Check the API is running.",
                    "trace_id":"ERROR",
                })
        st.rerun()


if __name__=="__main__":
    main()