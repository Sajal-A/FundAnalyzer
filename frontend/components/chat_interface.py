"""
frontend/components/chat_interface.py
──────────────────────────────────────
Chat interface component for user queries and responses.
"""

import streamlit as st
from datetime import datetime
from typing import Optional


def render_chat_interface():
    """Render the chat interface component."""
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 💬 Chat")
    with col2:
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()
    
    # Display conversation history
    for msg in st.session_state.get("messages", []):
        if msg["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.write(msg["content"])
                st.caption(msg.get("timestamp", ""))
        else:
            with st.chat_message("assistant", avatar="🤖"):
                if isinstance(msg["content"], dict):
                    response = msg["content"]
                    st.write(f"**Trace ID:** {response.get('trace_id')}")
                    st.write(f"**Confidence:** {response.get('overall_confidence', {}).get('level')}")
                    st.write(f"**Latency:** {response.get('latency_ms')} ms")
                else:
                    st.write(msg["content"])
                st.caption(msg.get("timestamp", ""))


def render_suggested_prompts():
    """Render suggested prompt buttons."""
    st.markdown("**Quick Prompts:**")
    
    prompts = [
        "Why did performance decline?",
        "Compare to peer funds",
        "Sector breakdown analysis",
        "Risk assessment for this period",
    ]
    
    cols = st.columns(len(prompts))
    selected = None
    
    for idx, prompt in enumerate(prompts):
        with cols[idx]:
            if st.button(prompt, use_container_width=True, key=f"prompt_{idx}"):
                selected = prompt
    
    return selected
