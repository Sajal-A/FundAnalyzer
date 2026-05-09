"""
frontend/components/orchestration_animation.py
───────────────────────────────────────────────
Orchestration animation showing parallel agent execution.
"""

import streamlit as st
import time
import plotly.graph_objects as go


def render_orchestration_animation():
    """Render the orchestration animation showing agent execution flow."""
    
    st.markdown("#### Agent Orchestration Flow")
    
    # Create columns for agent visualization
    col1, col2, col3, col4, col5 = st.columns(5)
    
    agents = [
        {"name": "Performance\nAgent", "status": "running"},
        {"name": "Flow\nAgent", "status": "running"},
        {"name": "Market\nAgent", "status": "running"},
        {"name": "Competitor\nAgent", "status": "running"},
        {"name": "Recommendation\nAgent", "status": "waiting"},
    ]
    
    cols = [col1, col2, col3, col4, col5]
    
    # Animate agent execution
    progress_placeholder = st.empty()
    
    for i in range(101):
        with progress_placeholder.container():
            for idx, (agent, col) in enumerate(zip(agents, cols)):
                with col:
                    if idx < 4:  # Group A agents
                        progress = min(100, i + (idx * 5))
                        if progress < 80:
                            st.markdown(f"""
                            <div style='text-align: center; padding: 10px; background: #e3f2fd; border-radius: 5px;'>
                                <h4>{agent['name']}</h4>
                                <p style='color: #1976d2;'>🔄 Running</p>
                                <div style='background: #ccc; height: 4px; border-radius: 2px; overflow: hidden;'>
                                    <div style='background: #1976d2; height: 100%; width: {progress}%;'></div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div style='text-align: center; padding: 10px; background: #c8e6c9; border-radius: 5px;'>
                                <h4>{agent['name']}</h4>
                                <p style='color: #388e3c;'>✅ Completed</p>
                                <div style='background: #ccc; height: 4px; border-radius: 2px; overflow: hidden;'>
                                    <div style='background: #388e3c; height: 100%; width: 100%;'></div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:  # Recommendation agent (waits)
                        if i > 80:
                            if i < 95:
                                st.markdown(f"""
                                <div style='text-align: center; padding: 10px; background: #fff3e0; border-radius: 5px;'>
                                    <h4>{agent['name']}</h4>
                                    <p style='color: #f57c00;'>⏳ Running</p>
                                    <div style='background: #ccc; height: 4px; border-radius: 2px; overflow: hidden;'>
                                        <div style='background: #f57c00; height: 100%; width: {i - 80}%;'></div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                <div style='text-align: center; padding: 10px; background: #c8e6c9; border-radius: 5px;'>
                                    <h4>{agent['name']}</h4>
                                    <p style='color: #388e3c;'>✅ Completed</p>
                                    <div style='background: #ccc; height: 4px; border-radius: 2px; overflow: hidden;'>
                                        <div style='background: #388e3c; height: 100%; width: 100%;'></div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div style='text-align: center; padding: 10px; background: #f3e5f5; border-radius: 5px;'>
                                <h4>{agent['name']}</h4>
                                <p style='color: #7b1fa2;'>⏸️ Waiting</p>
                                <div style='background: #ccc; height: 4px; border-radius: 2px; overflow: hidden;'>
                                    <div style='background: #ccc; height: 100%; width: 0%;'></div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
        
        if i < 100:
            time.sleep(0.02)  # Smooth animation
    
    # Show completion info
    st.success("✅ All agents completed execution!")
    
    st.markdown("**Execution Summary:**")
    summary_cols = st.columns(4)
    
    with summary_cols[0]:
        st.metric("Total Agents", "5", "All Completed")
    with summary_cols[1]:
        st.metric("Parallel Group", "4 agents", "Group A")
    with summary_cols[2]:
        st.metric("Sequential", "1 agent", "Recommendation")
    with summary_cols[3]:
        st.metric("Total Time", "~2.3s", "Estimated")


def render_execution_timeline():
    """Render a timeline of agent execution."""
    
    st.markdown("#### Execution Timeline")
    
    # Sample timeline data
    timeline_data = [
        {"Agent": "Performance", "Start": 0, "Duration": 800},
        {"Agent": "Flow", "Start": 0, "Duration": 750},
        {"Agent": "Market", "Start": 0, "Duration": 900},
        {"Agent": "Competitor", "Start": 0, "Duration": 850},
        {"Agent": "Recommendation", "Start": 900, "Duration": 500},
    ]
    
    fig = go.Figure()
    
    colors = ["#1976d2", "#1976d2", "#1976d2", "#1976d2", "#f57c00"]
    
    for idx, task in enumerate(timeline_data):
        fig.add_trace(go.Bar(
            y=[task["Agent"]],
            x=[task["Duration"]],
            name=task["Agent"],
            orientation="h",
            marker=dict(color=colors[idx]),
            showlegend=False,
        ))
    
    fig.update_layout(
        title="Agent Execution Timeline",
        xaxis_title="Duration (ms)",
        yaxis_title="Agent",
        barmode="overlay",
        height=300,
        showlegend=False,
    )
    
    st.plotly_chart(fig, use_container_width=True)
