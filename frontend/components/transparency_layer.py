"""
frontend/components/transparency_layer.py
──────────────────────────────────────────
Transparency and audit trail component showing confidence, checkpoints, and agent execution.
"""

import streamlit as st
from typing import Dict, Any, Optional
from utils.api_client import APIClient
import pandas as pd


def render_transparency_layer(
    response: Dict[str, Any],
    trace_id: Optional[str],
    api_client: APIClient
):
    """Render the transparency layer with confidence badges and audit trail."""
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Confidence badge
    with col1:
        confidence = response.get("overall_confidence", {})
        conf_score = confidence.get("score", 0)
        conf_level = confidence.get("level", "MEDIUM")
        
        if conf_score >= 0.8:
            st.success(f"✅ Confidence: {conf_level} ({conf_score:.2f})")
        elif conf_score >= 0.6:
            st.warning(f"⚠️ Confidence: {conf_level} ({conf_score:.2f})")
        else:
            st.error(f"❌ Confidence: {conf_level} ({conf_score:.2f})")
    
    # Checkpoint tier
    with col2:
        checkpoint = response.get("checkpoint_tier", "STANDARD")
        st.info(f"📍 Checkpoint: {checkpoint}")
    
    # Latency
    with col3:
        latency_ms = response.get("latency_ms", 0)
        st.metric("Latency", f"{latency_ms} ms")
    
    # Trace ID
    with col4:
        st.code(trace_id[:16] + "..." if trace_id else "N/A")
    
    st.divider()
    
    # Agent execution pills
    st.markdown("### 🤖 Agent Execution")
    
    if trace_id and st.button("📥 Fetch Audit Data", key="fetch_audit"):
        try:
            with st.spinner("Loading audit data..."):
                audit = api_client.get_audit(trace_id)
                
                agent_calls = audit.get("agent_calls", [])
                
                if agent_calls:
                    # Create agent pills
                    agent_cols = st.columns(min(4, len(agent_calls)))
                    
                    for idx, call in enumerate(agent_calls):
                        with agent_cols[idx % 4]:
                            agent_name = call.get("agent_name", "Unknown")
                            latency = call.get("latency_ms", 0)
                            confidence = call.get("confidence", "N/A")
                            
                            with st.container(border=True):
                                st.markdown(f"**{agent_name}**")
                                st.caption(f"⏱️ {latency}ms | 🎯 {confidence}")
                else:
                    st.info("No agent calls recorded")
        
        except Exception as e:
            st.error(f"Failed to load audit data: {str(e)}")
    
    st.divider()
    
    # Show audit trail
    st.markdown("### 📋 Show Your Work - Audit Trail")
    
    audit_tabs = st.tabs(["Agent Calls", "Confidence Factors", "Conflicts", "Data Sources"])
    
    with audit_tabs[0]:
        render_agent_calls_detail(response, trace_id, api_client)
    
    with audit_tabs[1]:
        render_confidence_factors(response)
    
    with audit_tabs[2]:
        render_conflicts_detail(response)
    
    with audit_tabs[3]:
        render_sources_detail(response)


def render_agent_calls_detail(response: Dict[str, Any], trace_id: Optional[str], api_client: APIClient):
    """Render detailed agent call information."""
    
    st.markdown("#### Agent Calls Trace")
    
    if trace_id:
        try:
            audit = api_client.get_audit(trace_id)
            agent_calls = audit.get("agent_calls", [])
            
            if agent_calls:
                df_agents = pd.DataFrame([
                    {
                        "Agent": call.get("agent_name", "Unknown"),
                        "Latency (ms)": call.get("latency_ms", 0),
                        "Confidence": call.get("confidence", "N/A"),
                        "Status": call.get("status", "completed"),
                        "Called At": call.get("called_at", "N/A"),
                    }
                    for call in agent_calls
                ])
                
                st.dataframe(df_agents, use_container_width=True, hide_index=True)
                
                # Parallel vs sequential info
                st.info("ℹ️ Group A agents (Performance, Flow, Market, Competitor) run in parallel. Recommendation agent runs sequentially.")
            else:
                st.info("No agent call data available")
        
        except Exception as e:
            st.warning(f"Could not fetch detailed agent calls: {str(e)}")
    else:
        st.warning("No trace ID available")


def render_confidence_factors(response: Dict[str, Any]):
    """Render 5-factor weighted confidence score breakdown."""
    
    st.markdown("#### Confidence Score Breakdown")
    
    # Get confidence details
    confidence_details = response.get("show_your_work", {}).get("confidence", {})
    
    if isinstance(confidence_details, dict) and confidence_details:
        factors = confidence_details.get("factors", {})
        
        if factors:
            factor_df = pd.DataFrame([
                {
                    "Factor": factor,
                    "Weight %": details.get("weight", 0),
                    "Score": details.get("score", 0),
                }
                for factor, details in factors.items()
            ])
            
            st.dataframe(factor_df, use_container_width=True, hide_index=True)
            
            # Visual representation
            import plotly.graph_objects as go
            fig = go.Figure(data=[
                go.Bar(
                    x=factor_df["Factor"],
                    y=factor_df["Score"],
                    marker=dict(color=factor_df["Score"], colorscale="RdYlGn", showscale=False)
                )
            ])
            fig.update_layout(
                title="Confidence Factor Scores",
                xaxis_title="Factor",
                yaxis_title="Score",
                height=300,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No detailed confidence factors available")
    else:
        st.info("Confidence factors not available in this response mode")


def render_conflicts_detail(response: Dict[str, Any]):
    """Render inter-agent conflict resolution information."""
    
    st.markdown("#### Agent Conflicts & Resolution")
    
    conflicts = response.get("conflicts_summary", [])
    
    if conflicts:
        for idx, conflict in enumerate(conflicts):
            with st.expander(f"Conflict {idx+1}: {conflict.get('topic', 'N/A')}", expanded=(idx == 0)):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Topic:** {conflict.get('topic', 'N/A')}")
                    st.markdown(f"**Resolution:** {conflict.get('resolution', 'N/A')}")
                
                with col2:
                    st.markdown(f"**Winning Agent:** {conflict.get('winning_agent', 'N/A')}")
                    st.markdown(f"**Confidence:** {conflict.get('confidence', 'N/A')}")
    else:
        st.success("✅ No conflicts detected - all agents agreed!")


def render_sources_detail(response: Dict[str, Any]):
    """Render data source hierarchy information."""
    
    st.markdown("#### Data Source Hierarchy")
    
    st.markdown("""
    **Tier 1 - Primary (Highest Priority):**
    - SQLite Database: Live fund data, performance records
    
    **Tier 2 - Secondary:**
    - ChromaDB Vector Store: Historical context, semantic search results
    
    **Tier 3 - Tertiary:**
    - Market Intelligence APIs: Real-time market data, peer benchmarks
    
    **Source Attribution:**
    - Each recommendation is traced back to its data sources
    - Confidence scores reflect source reliability
    """)
    
    # Source breakdown for this analysis
    response_sources = response.get("show_your_work", {}).get("sources", [])
    
    if response_sources:
        st.markdown("**Sources Used in This Analysis:**")
        for source in response_sources:
            st.write(f"• {source}")
    else:
        st.info("Source details not available in this response mode")
