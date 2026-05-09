"""
frontend/__init__.py
───────────────────
Frontend module initialization.
"""

__version__ = "1.0.0"
__author__ = "Fund Performance Diagnostic AI Team"
__description__ = "Interactive Streamlit UI for Fund Performance Diagnostic AI"

from frontend.utils import APIClient, StateManager
from frontend.components import (
    render_chat_interface,
    render_diagnostic_response,
    render_transparency_layer,
    render_orchestration_animation,
)

__all__ = [
    "APIClient",
    "StateManager",
    "render_chat_interface",
    "render_diagnostic_response",
    "render_transparency_layer",
    "render_orchestration_animation",
]
