"""
frontend/config.py
──────────────────
Configuration for the Streamlit frontend.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "60"))

# Streamlit Configuration
APP_TITLE = "Fund Performance Diagnostic AI"
APP_ICON = "📊"

# UI Configuration
DEFAULT_FUND_ID = "GEF001"
DEFAULT_PERIOD = "2026-Q1"
DEFAULT_MODE = "standard"

# Suggested prompts
SUGGESTED_PROMPTS = [
    "Why did our Global Equity Fund slow down this quarter?",
    "Compare our performance to peers in the same category",
    "What are the main risk factors affecting this fund?",
    "Give me a sector-by-sector breakdown for this period",
    "Analyze the fund flow trends for this period",
]

# Follow-up suggestions
FOLLOWUP_SUGGESTIONS = [
    "Why did tech drag on performance?",
    "What about EMEA region?",
    "Which action should we take first?",
    "How does this compare to 2026-Q2?",
    "What are the confidence factors?",
]

# Color palette
COLORS = {
    "primary": "#1976d2",
    "secondary": "#1565c0",
    "success": "#4caf50",
    "warning": "#ff9800",
    "error": "#f44336",
    "light_bg": "#f5f5f5",
    "light_blue": "#e3f2fd",
}

# Confidence thresholds
CONFIDENCE_THRESHOLDS = {
    "high": 0.8,
    "medium": 0.6,
    "low": 0.0,
}

# Animation settings
ANIMATION_SPEED = 0.02  # seconds per frame
ANIMATION_TOTAL_FRAMES = 100

# Cache settings
CACHE_TTL = 3600  # seconds
