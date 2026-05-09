"""
api/models.py
──────────────
Pydantic v2 request and response models for the FastAPI layer.
"""

from pydantic import BaseModel, Field
from typing import Any


# ── Request Models ────────────────────────────────────────────────────────────

class DiagnoseRequest(BaseModel):
    query:   str    = Field(..., description="Natural language query about fund performance")
    fund_id: str    = Field(default="GEF001", description="Fund identifier")
    period:  str    = Field(default="2026-Q1", description="Period: e.g. '2026-Q1' or '2026-01:2026-03'")
    user_id: str    = Field(default="advisor", description="Requesting user identifier")
    mode:    str    = Field(default="standard", description="'standard' or 'detailed' (Show Your Work)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "query":   "Why did our Global Equity Fund slow down this quarter?",
                "fund_id": "GEF001",
                "period":  "2026-Q1",
                "user_id": "advisor_jsmith",
                "mode":    "standard",
            }
        }
    }


class ApproveRequest(BaseModel):
    approved_by: str = Field(..., description="User ID of the approver")


# ── Response Models ───────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status:  str
    version: str
    db:      str
    vector_store: str


class DiagnoseResponse(BaseModel):
    trace_id:           str
    fund_id:            str
    period:             str
    generated_at:       str
    latency_ms:         int
    overall_confidence: dict[str, Any]
    root_cause:         dict[str, Any]
    peer_comparison:    dict[str, Any]
    recommendations:    list[dict[str, Any]]
    conflicts_detected: bool
    conflicts_summary:  list[dict[str, Any]]
    disclaimer:         str
    show_your_work:     dict[str, Any] | None = None


class AuditResponse(BaseModel):
    trace_id:       str
    session:        dict[str, Any]
    agent_calls:    list[dict[str, Any]]
    conflicts:      list[dict[str, Any]]


class ErrorResponse(BaseModel):
    error:   str
    detail:  str | None = None
    trace_id: str | None = None