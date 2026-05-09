"""
frontend/utils/api_client.py
──────────────────────────────
HTTP client for communicating with the FastAPI backend.
"""

import requests
import json
from typing import Optional, Dict, Any
from loguru import logger


class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
        })
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health status."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise
    
    def diagnose(
        self,
        query: str,
        fund_id: str = "GEF001",
        period: str = "2026-Q1",
        user_id: str = "advisor",
        mode: str = "standard"
    ) -> Dict[str, Any]:
        """Submit a diagnostic query and get response."""
        try:
            payload = {
                "query": query,
                "fund_id": fund_id,
                "period": period,
                "user_id": user_id,
                "mode": mode,
            }
            
            response = self.session.post(
                f"{self.base_url}/diagnose",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Diagnose request failed: {e}")
            raise
    
    def get_audit(self, trace_id: str) -> Dict[str, Any]:
        """Retrieve audit record for a trace."""
        try:
            response = self.session.get(
                f"{self.base_url}/audit/{trace_id}",
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Get audit failed: {e}")
            raise
    
    def get_full_audit(self, trace_id: str) -> Dict[str, Any]:
        """Retrieve full audit trail with detailed Show Your Work."""
        try:
            response = self.session.get(
                f"{self.base_url}/audit/{trace_id}/detail",
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Get full audit failed: {e}")
            raise
    
    def approve_recommendation(
        self,
        trace_id: str,
        approved_by: str
    ) -> Dict[str, Any]:
        """Approve a recommendation."""
        try:
            payload = {"approved_by": approved_by}
            response = self.session.post(
                f"{self.base_url}/audit/{trace_id}/approve",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Approve recommendation failed: {e}")
            raise
