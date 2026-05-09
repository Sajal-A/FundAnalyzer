"""
api/main.py
────────────
FastAPI application — defines all API routes.

Endpoints:
  POST /diagnose              — Main diagnostic query
  GET  /audit/{trace_id}      — Retrieve audit record
  GET  /audit/{trace_id}/detail — Full Show Your Work audit chain
  POST /audit/{trace_id}/approve — Human sign-off
  GET  /health                — Health check
"""

import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from api.models import (
    DiagnoseRequest,
    DiagnoseResponse,
    AuditResponse,
    ApproveRequest,
    HealthResponse,
    ErrorResponse,
)
from agents.orchestrator import run_orchestrator
from core.audit import get_audit_record, get_full_audit, log_approval
from core.config import settings
from core.exceptions import OrchestratorError, DataNotFoundError
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
print(f"api_key: ", api_key)


# ── App Initialization ────────────────────────────────────────────────────────
app = FastAPI(
    title       = "Fund Performance Diagnostic AI",
    description = "Multi-agent AI system for autonomous fund performance diagnosis.",
    version     = "1.0.0",
    docs_url    = "/docs",
    redoc_url   = "/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],   # Restrict in production
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check():
    """Check that the API, database, and vector store are operational."""
    # Check SQLite
    db_status = "ok"
    try:
        conn = sqlite3.connect(settings.db_path)
        conn.execute("SELECT 1")
        conn.close()
    except Exception:
        db_status = "error"

    # Check ChromaDB
    vs_status = "ok"
    try:
        from core.vector_store import get_chroma_client
        get_chroma_client().heartbeat()
    except Exception:
        vs_status = "error"

    return HealthResponse(
        status       = "ok" if db_status == "ok" and vs_status == "ok" else "degraded",
        version      = "1.0.0",
        db           = db_status,
        vector_store = vs_status,
    )


@app.post(
    "/diagnose",
    response_model  = DiagnoseResponse,
    status_code     = status.HTTP_200_OK,
    tags            = ["Diagnostics"],
    summary         = "Run a fund performance diagnostic query",
)
def diagnose(request: DiagnoseRequest):
    """
    Main endpoint — accepts a natural language query and returns
    a full AI-generated fund performance diagnostic.

    Set `mode` to `detailed` to include the full Show Your Work audit chain.
    """
    logger.info(
        f"Received diagnostic request: fund={request.fund_id}, "
        f"period={request.period}, user={request.user_id}"
    )

    try:
        result = run_orchestrator(
            query    = request.query,
            fund_id  = request.fund_id,
            period   = request.period,
            user_id  = request.user_id,
            detailed = (request.mode == "detailed"),
        )
        return result

    except OrchestratorError as e:
        logger.error(f"Orchestrator error: {e}")
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail      = str(e),
        )
    except Exception as e:
        logger.exception(f"Unexpected error in /diagnose: {e}")
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail      = f"An unexpected error occurred: {e}",
        )


@app.get(
    "/audit/{trace_id}",
    response_model = AuditResponse,
    tags           = ["Audit & Transparency"],
    summary        = "Retrieve the audit record for a diagnostic session",
)
def get_audit(trace_id: str):
    """
    Returns the full audit package for a given trace_id:
    session record, all agent call logs, and any conflict records.
    """
    audit = get_full_audit(trace_id)
    if not audit:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = f"No audit record found for trace_id: {trace_id}",
        )
    return AuditResponse(
        trace_id    = trace_id,
        session     = dict(audit["session"]),
        agent_calls = [dict(c) for c in audit["agent_calls"]],
        conflicts   = [dict(c) for c in audit["conflicts"]],
    )


@app.post(
    "/audit/{trace_id}/approve",
    tags    = ["Audit & Transparency"],
    summary = "Record human sign-off (approval) for a diagnostic output",
)
def approve_output(trace_id: str, request: ApproveRequest):
    """
    Records a human approval for the specified trace.
    Used for AMBER and RED checkpoint tier outputs before client delivery.
    """
    record = get_audit_record(trace_id)
    if not record:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = f"No audit record found for trace_id: {trace_id}",
        )

    log_approval(
        trace_id        = trace_id,
        approved_by     = request.approved_by,
        checkpoint_tier = dict(record).get("checkpoint_tier", "AMBER"),
    )

    logger.info(
        f"Output approved: trace_id={trace_id}, approved_by={request.approved_by}"
    )
    return {
        "message":     "Output approved successfully.",
        "trace_id":    trace_id,
        "approved_by": request.approved_by,
    }