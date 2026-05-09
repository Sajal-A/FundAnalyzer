"""
frontend/styles/theme.py
────────────────────────
Custom theme and styling for the Streamlit UI.
"""

import streamlit as st


def apply_theme():
    """Apply custom theme to Streamlit app."""
    
    st.markdown("""
    <style>
    /* Main container */
    .main {
        max-width: 1400px;
    }
    
    /* Header styling */
    h1 {
        color: #1976d2;
        border-bottom: 3px solid #1976d2;
        padding-bottom: 10px;
    }
    
    h2 {
        color: #1565c0;
        margin-top: 20px;
    }
    
    h3 {
        color: #1976d2;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1rem;
        font-weight: 600;
    }
    
    /* Card styling */
    .stMetric {
        background: #f5f5f5;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #1976d2;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #1976d2;
        color: white;
        border-radius: 4px;
        border: none;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #1565c0;
        transform: translateY(-2px);
    }
    
    /* Alert boxes */
    .stSuccess {
        background: #c8e6c9;
        border-radius: 4px;
        padding: 10px;
    }
    
    .stWarning {
        background: #fff3e0;
        border-radius: 4px;
        padding: 10px;
    }
    
    .stError {
        background: #ffcdd2;
        border-radius: 4px;
        padding: 10px;
    }
    
    .stInfo {
        background: #e3f2fd;
        border-radius: 4px;
        padding: 10px;
    }
    
    /* Expander styling */
    .streamlit-expanderContent {
        background: #fafafa;
        border-radius: 4px;
    }
    
    /* Text input styling */
    .stTextInput input, .stTextArea textarea {
        border: 2px solid #e0e0e0;
        border-radius: 4px;
        padding: 10px;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border: 2px solid #1976d2;
        outline: none;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border-radius: 4px;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #f5f5f5;
    }
    
    /* Link styling */
    a {
        color: #1976d2;
        text-decoration: none;
    }
    
    a:hover {
        text-decoration: underline;
    }
    
    /* Divider */
    hr {
        border: 0;
        height: 1px;
        background: #e0e0e0;
    }
    
    /* Caption text */
    .streamlit-caption {
        color: #757575;
        font-size: 0.85rem;
    }
    
    /* Custom badge styles */
    .confidence-badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .confidence-high {
        background: #c8e6c9;
        color: #1b5e20;
    }
    
    .confidence-medium {
        background: #fff3e0;
        color: #e65100;
    }
    
    .confidence-low {
        background: #ffcdd2;
        color: #b71c1c;
    }
    
    /* Agent pill styling */
    .agent-pill {
        display: inline-block;
        padding: 8px 15px;
        margin: 5px;
        border-radius: 20px;
        background: #e3f2fd;
        border: 2px solid #1976d2;
        color: #1565c0;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    /* Status indicator */
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 5px;
    }
    
    .status-success {
        background: #4caf50;
    }
    
    .status-warning {
        background: #ff9800;
    }
    
    .status-error {
        background: #f44336;
    }
    
    /* Animation */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    </style>
    """, unsafe_allow_html=True)
