"""
frontend/utils/state_manager.py
────────────────────────────────
Manages Streamlit session state and conversation persistence.
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional


class StateManager:
    """Manages application state across Streamlit reruns."""
    
    def __init__(self):
        self.state = {}
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get full conversation history."""
        return self.state.get("messages", [])
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None) -> None:
        """Add message to conversation history."""
        if "messages" not in self.state:
            self.state["messages"] = []
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }
        
        if metadata:
            message.update(metadata)
        
        self.state["messages"].append(message)
    
    def clear_history(self) -> None:
        """Clear conversation history."""
        self.state["messages"] = []
    
    def get_current_context(self) -> Dict[str, Any]:
        """Get current analysis context."""
        if not self.state.get("messages"):
            return {}
        
        # Get last assistant response
        for msg in reversed(self.state["messages"]):
            if msg["role"] == "assistant" and isinstance(msg["content"], dict):
                return msg["content"]
        
        return {}
    
    def set_current_response(self, response: Dict[str, Any]) -> None:
        """Set current diagnostic response."""
        self.state["current_response"] = response
    
    def get_current_response(self) -> Optional[Dict[str, Any]]:
        """Get current diagnostic response."""
        return self.state.get("current_response")
    
    def export_history(self) -> str:
        """Export conversation history as JSON."""
        return json.dumps(self.state.get("messages", []), indent=2)
    
    def export_summary(self) -> str:
        """Export conversation summary."""
        messages = self.state.get("messages", [])
        summary = []
        
        for msg in messages:
            timestamp = msg.get("timestamp", "")
            role = msg.get("role", "unknown")
            
            if role == "user":
                content_preview = msg.get("content", "")[:100]
                summary.append(f"[{timestamp}] User: {content_preview}...")
            else:
                if isinstance(msg.get("content"), dict):
                    trace_id = msg["content"].get("trace_id", "N/A")
                    confidence = msg["content"].get("overall_confidence", {}).get("level", "N/A")
                    summary.append(f"[{timestamp}] Assistant: Trace {trace_id} (Confidence: {confidence})")
                else:
                    summary.append(f"[{timestamp}] Assistant: Response received")
        
        return "\n".join(summary)
