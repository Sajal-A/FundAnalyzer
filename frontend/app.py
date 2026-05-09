"""
frontend/app.py
──────────────────
Main Streamlit UI for Fund Performance Diagnostic AI.

Features:
  - Chat interface with suggested prompts
  - Live orchestration animation showing parallel agents
  - Multi-tab diagnostic response (Overview, Performance, Peers, Recommendations)
  - Full conversation history
  - Transparency layer with confidence badges, agent pills, audit trail
  - Follow-up question suggestions
"""

import streamlit as st
from datetime import datetime
import asyncio
import json
from pathlib import Path

from components.chat_interface import render_chat_interface
from components.diagnostic_response import render_diagnostic_response
from components.transparency_layer import render_transparency_layer
from components.orchestration_animation import render_orchestration_animation
from utils.api_client import APIClient
from utils.state_manager import StateManager
from styles.theme import apply_theme

# ── Page Configuration ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Fund Performance Diagnostic AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()

# ── Session State Initialization ───────────────────────────────────────────────
state_manager = StateManager()
api_client = APIClient(base_url="http://localhost:8000")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_response" not in st.session_state:
    st.session_state.current_response = None
if "trace_id" not in st.session_state:
    st.session_state.trace_id = None
if "agent_execution_data" not in st.session_state:
    st.session_state.agent_execution_data = None
if "fund_id" not in st.session_state:
    st.session_state.fund_id = "GEF001"
if "period" not in st.session_state:
    st.session_state.period = "2026-Q1"
if "user_id" not in st.session_state:
    st.session_state.user_id = "advisor"

# ── Header & Branding ─────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("# 📊 Fund Performance Diagnostic AI")
    st.markdown("<p style='text-align: center; color: gray;'>Multi-agent intelligence for fund analysis</p>", unsafe_allow_html=True)

# ── Sidebar: Configuration ─────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")
    
    st.session_state.fund_id = st.selectbox(
        "Fund ID",
        ["GEF001", "GEF002", "GEF003"],
        index=0,
        help="Select the fund to analyze"
    )
    
    st.session_state.period = st.selectbox(
        "Period",
        ["2026-Q1", "2026-Q2", "2026-Q3", "2026-Q4"],
        index=0,
        help="Select analysis period"
    )
    
    st.session_state.user_id = st.text_input(
        "User ID",
        value=st.session_state.user_id,
        help="Your identifier"
    )
    
    # Mode selector
    mode = st.radio(
        "Analysis Mode",
        ["Standard", "Detailed (Show Your Work)"],
        help="Standard shows summary, Detailed shows full audit trail"
    )
    
    # Health check
    st.divider()
    if st.button("🔍 Health Check", use_container_width=True):
        try:
            health = api_client.health_check()
            st.success(f"✅ API Status: {health.get('status')}")
            st.info(f"DB: {health.get('db')} | Vector Store: {health.get('vector_store')}")
        except Exception as e:
            st.error(f"❌ API Error: {str(e)}")
    
    # Clear history
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_response = None
        st.rerun()
    
    st.divider()
    st.caption("📝 Fund Performance Diagnostic v1.0")

# ── Main Content Area ──────────────────────────────────────────────────────────
main_col1, main_col2 = st.columns([2, 1])

with main_col1:
    st.markdown("### 💬 Chat Interface")
    
    # Suggested prompts
    st.markdown("**Suggested Prompts:**")
    suggested_prompts = [
        "Why did our Global Equity Fund slow down this quarter?",
        "Compare our performance to peers in the same category",
        "What are the main risk factors affecting this fund?",
        "Give me a sector-by-sector breakdown for this period",
    ]
    
    prompt_cols = st.columns(2)
    selected_prompt = None
    for idx, prompt in enumerate(suggested_prompts):
        with prompt_cols[idx % 2]:
            if st.button(f"💡 {prompt[:40]}...", use_container_width=True, key=f"prompt_{idx}"):
                selected_prompt = prompt
    
    # Chat input
    user_input = st.text_area(
        "Your Query",
        placeholder="Ask about fund performance, compare to peers, request recommendations...",
        height=100,
        label_visibility="collapsed"
    )
    
    # Submit button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        submit_button = st.button("🚀 Analyze", use_container_width=True)
    with col2:
        clear_input = st.button("Clear", use_container_width=True)
    with col3:
        export_button = st.button("📥 Export", use_container_width=True)
    
    if clear_input:
        st.rerun()
    
    # Use selected prompt or text input
    query = selected_prompt or user_input
    
    # ── Submit Query ───────────────────────────────────────────────────────────
    if submit_button and query.strip():
        with st.spinner("🔄 Orchestrating analysis..."):
            try:
                # Show orchestration animation
                st.markdown("### 🎬 Agent Orchestration")
                animation_placeholder = st.empty()
                
                with animation_placeholder.container():
                    render_orchestration_animation()
                
                # Call API
                mode_str = "detailed" if "Detailed" in mode else "standard"
                response = api_client.diagnose(
                    query=query,
                    fund_id=st.session_state.fund_id,
                    period=st.session_state.period,
                    user_id=st.session_state.user_id,
                    mode=mode_str
                )
                
                # Store response
                st.session_state.current_response = response
                st.session_state.trace_id = response.get("trace_id")
                
                # Add to conversation history
                st.session_state.messages.append({
                    "role": "user",
                    "content": query,
                    "timestamp": datetime.now().isoformat()
                })
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now().isoformat()
                })
                
                animation_placeholder.empty()
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # ── Display Conversation History ───────────────────────────────────────────
    if st.session_state.messages:
        st.markdown("### 📜 Conversation History")
        for idx, msg in enumerate(st.session_state.messages):
            if msg["role"] == "user":
                st.info(f"**You:** {msg['content']}")
            else:
                # Just show summary in history
                st.success("**Assistant:** Analysis complete - see diagnostic response below")

with main_col2:
    st.markdown("### 📊 Response Metadata")
    if st.session_state.current_response:
        resp = st.session_state.current_response
        st.metric("Confidence", f"{resp.get('overall_confidence', {}).get('level', 'N/A')}")
        st.metric("Latency", f"{resp.get('latency_ms', 0)} ms")
        st.metric("Trace ID", resp.get('trace_id', 'N/A')[:12] + "...")

# ── Diagnostic Response Tabs ───────────────────────────────────────────────────
if st.session_state.current_response:
    st.markdown("---")
    st.markdown("### 📈 Diagnostic Response")
    
    render_diagnostic_response(st.session_state.current_response)

# ── Transparency Layer ─────────────────────────────────────────────────────────
if st.session_state.current_response:
    st.markdown("---")
    st.markdown("### 🔍 Transparency & Audit Trail")
    
    render_transparency_layer(
        st.session_state.current_response,
        st.session_state.trace_id,
        api_client
    )

# ── Follow-up Questions ────────────────────────────────────────────────────────
if st.session_state.current_response:
    st.markdown("---")
    st.markdown("### 💬 Follow-up Questions")
    
    follow_up_suggestions = [
        "Why did tech drag on performance?",
        "What about EMEA region?",
        "Which action should we take first?",
        "How does this compare to 2026-Q2?",
        "What are the confidence factors?",
    ]
    
    followup_cols = st.columns(len(follow_up_suggestions))
    for idx, suggestion in enumerate(follow_up_suggestions):
        with followup_cols[idx]:
            if st.button(suggestion, use_container_width=True, key=f"followup_{idx}"):
                st.session_state.messages.append({
                    "role": "user",
                    "content": suggestion,
                    "timestamp": datetime.now().isoformat()
                })
                st.rerun()
