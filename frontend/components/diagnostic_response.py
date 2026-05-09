"""
frontend/components/diagnostic_response.py
───────────────────────────────────────────
Diagnostic response component with Overview, Performance, Peers, and Recommendations tabs.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List
import plotly.graph_objects as go
import plotly.express as px


def render_diagnostic_response(response: Dict[str, Any]):
    """Render the diagnostic response with multiple tabs."""
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Overview", "📊 Performance", "👥 Peers", "💡 Recommendations"])
    
    # ── TAB 1: OVERVIEW ────────────────────────────────────────────────────────
    with tab1:
        render_overview_tab(response)
    
    # ── TAB 2: PERFORMANCE ─────────────────────────────────────────────────────
    with tab2:
        render_performance_tab(response)
    
    # ── TAB 3: PEERS ───────────────────────────────────────────────────────────
    with tab3:
        render_peers_tab(response)
    
    # ── TAB 4: RECOMMENDATIONS ────────────────────────────────────────────────
    with tab4:
        render_recommendations_tab(response)


def render_overview_tab(response: Dict[str, Any]):
    """Render the Overview tab with key metrics and root cause."""
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Display key metrics
    with col1:
        confidence = response.get("overall_confidence", {})
        st.metric(
            "Overall Confidence",
            confidence.get("level", "N/A"),
            f"Score: {confidence.get('score', 0):.2f}"
        )
    
    with col2:
        st.metric(
            "Latency",
            f"{response.get('latency_ms', 0)} ms"
        )
    
    with col3:
        st.metric(
            "Fund ID",
            response.get("fund_id", "N/A")
        )
    
    with col4:
        st.metric(
            "Period",
            response.get("period", "N/A")
        )
    
    # Root cause analysis
    st.markdown("### 🎯 Root Cause Analysis")
    root_cause = response.get("root_cause", {})
    
    col1, col2 = st.columns([2, 1])
    with col1:
        if root_cause:
            st.markdown(f"**Primary Issue:** {root_cause.get('primary_issue', 'N/A')}")
            st.markdown(f"**Impact:** {root_cause.get('impact', 'N/A')}")
            
            if "contributing_factors" in root_cause:
                st.markdown("**Contributing Factors:**")
                for factor in root_cause.get("contributing_factors", []):
                    st.markdown(f"- {factor}")
        else:
            st.info("No root cause data available")
    
    with col2:
        severity = root_cause.get("severity", "MEDIUM")
        if severity == "HIGH":
            st.error(f"⚠️ {severity}")
        elif severity == "MEDIUM":
            st.warning(f"⚠️ {severity}")
        else:
            st.info(f"ℹ️ {severity}")
    
    # Macro headwinds and risk events
    st.markdown("### 📉 Macro Headwinds")
    headwinds = response.get("root_cause", {}).get("macro_headwinds", [])
    if headwinds:
        for headwind in headwinds:
            st.write(f"• {headwind}")
    else:
        st.info("No macro headwinds detected")
    
    st.markdown("### ⚡ Risk Events")
    risk_events = response.get("root_cause", {}).get("risk_events", [])
    if risk_events:
        for event in risk_events:
            st.write(f"• {event}")
    else:
        st.info("No risk events detected")


def render_performance_tab(response: Dict[str, Any]):
    """Render the Performance tab with monthly returns and sector attribution."""
    
    st.markdown("### 📈 Monthly Returns")
    
    # Sample monthly returns table
    monthly_data = response.get("root_cause", {}).get("monthly_returns", None)
    if monthly_data:
        df_returns = pd.DataFrame(monthly_data)
        st.dataframe(df_returns, use_container_width=True)
    else:
        # Display placeholder
        df = pd.DataFrame({
            "Month": ["2026-01", "2026-02", "2026-03"],
            "Return %": [1.2, -0.5, 2.1],
            "Benchmark %": [1.0, 0.2, 1.8],
        })
        st.dataframe(df, use_container_width=True)
    
    st.markdown("### 🏭 Sector Attribution")
    
    # Sector attribution chart
    sector_data = response.get("root_cause", {}).get("sector_attribution", None)
    if sector_data:
        fig = px.bar(
            sector_data,
            x="sector",
            y="contribution",
            title="Sector Contribution to Returns",
            color="contribution",
            color_continuous_scale="RdYlGn"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        # Display placeholder
        sectors = ["Tech", "Healthcare", "Financials", "Energy", "Consumer"]
        contributions = [0.85, 0.35, -0.12, -0.28, 0.20]
        fig = px.bar(
            x=sectors,
            y=contributions,
            title="Sector Contribution to Returns",
            labels={"x": "Sector", "y": "Contribution (%)"}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### 🌍 Regional & Channel Breakdown")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Regional Distribution:**")
        regions = pd.DataFrame({
            "Region": ["North America", "Europe", "Asia Pacific"],
            "Allocation %": [55, 30, 15]
        })
        st.dataframe(regions, use_container_width=True)
    
    with col2:
        st.markdown("**Channel Breakdown:**")
        channels = pd.DataFrame({
            "Channel": ["Direct", "Mutual", "ETF"],
            "Flow %": [40, 35, 25]
        })
        st.dataframe(channels, use_container_width=True)


def render_peers_tab(response: Dict[str, Any]):
    """Render the Peers tab with category ranking and strategy gap analysis."""
    
    st.markdown("### 👥 Category Ranking")
    
    # Peer comparison
    peer_comparison = response.get("peer_comparison", {})
    
    ranking_data = peer_comparison.get("rankings", None)
    if ranking_data:
        df_ranks = pd.DataFrame(ranking_data)
        st.dataframe(df_ranks, use_container_width=True)
    else:
        # Display placeholder
        df_ranks = pd.DataFrame({
            "Rank": [1, 2, 3, 4, 5],
            "Fund": ["PeerFund A", "PeerFund B", "GEF001", "PeerFund C", "PeerFund D"],
            "YTD Return %": [4.2, 3.8, 1.5, 1.2, 0.8],
            "Category Percentile": [95, 87, 25, 18, 10],
        })
        st.dataframe(df_ranks, use_container_width=True, hide_index=True)
    
    # Highlight our fund
    our_rank = peer_comparison.get("our_ranking", "N/A")
    st.info(f"**GEF001 Category Ranking:** {our_rank}")
    
    st.markdown("### 📊 Strategy Gap Analysis")
    
    gap_analysis = peer_comparison.get("strategy_gap", {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Performance Gap vs Peers:**")
        if gap_analysis:
            gap = gap_analysis.get("performance_gap", 0)
            if gap < 0:
                st.error(f"Underperforming by {abs(gap):.2f}%")
            else:
                st.success(f"Outperforming by {gap:.2f}%")
        else:
            st.warning("Gap data not available")
    
    with col2:
        st.markdown("**Strategic Differences:**")
        differences = gap_analysis.get("differences", [])
        if differences:
            for diff in differences:
                st.write(f"• {diff}")
        else:
            st.info("No significant strategic differences detected")


def render_recommendations_tab(response: Dict[str, Any]):
    """Render the Recommendations tab with actions and approval gates."""
    
    st.markdown("### 💡 Recommended Actions")
    
    recommendations = response.get("recommendations", [])
    
    if not recommendations:
        st.info("No recommendations at this time")
        return
    
    # Color mapping for approval status
    status_colors = {
        "GREEN": "✅ APPROVED",
        "AMBER": "⚠️ REVIEW REQUIRED",
        "RED": "❌ NOT RECOMMENDED",
    }
    
    for idx, rec in enumerate(recommendations):
        with st.expander(f"Action {idx+1}: {rec.get('title', 'N/A')}", expanded=(idx == 0)):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Description:** {rec.get('description', 'N/A')}")
                st.markdown(f"**Impact:** {rec.get('impact', 'N/A')}")
                
                st.markdown("**Rationale:**")
                rationale = rec.get("rationale", "")
                st.write(rationale)
                
                # Source citations
                sources = rec.get("sources", [])
                if sources:
                    st.markdown("**Supporting Agents:**")
                    for source in sources:
                        st.write(f"• {source}")
            
            with col2:
                # Approval status
                status = rec.get("approval_status", "AMBER")
                status_text = status_colors.get(status, status)
                
                if status == "GREEN":
                    st.success(status_text)
                elif status == "AMBER":
                    st.warning(status_text)
                else:
                    st.error(status_text)
                
                # Approval button
                if status != "GREEN":
                    if st.button(f"✅ Approve Action {idx+1}", key=f"approve_{idx}"):
                        st.success("Action approved!")
                        st.balloons()
