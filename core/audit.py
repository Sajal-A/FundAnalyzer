"""
core/audit.py
─────────────
Immutable audit trail — every orchestrator invocation is logged here.
Stored in the same SQLite database under the `audit_log` table.
"""

import json
import uuid
from datetime import datetime, timezone

from core.database import execute, query_all, query_one


def generate_trace_id() -> str:
    """Generate a unique trace ID for each orchestrator session."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    short = str(uuid.uuid4()).split("-")[0].upper()
    return f"FPD-{ts}-{short}"


def log_session_start(
    trace_id: str,
    user_id: str,
    query_raw: str,
    query_parsed: dict,
) -> None:
    """Create the audit record when a session begins."""
    execute(
        """
        INSERT INTO audit_log (
            trace_id, user_id, query_raw, query_parsed,
            status, created_at
        ) VALUES (?, ?, ?, ?, 'IN_PROGRESS', ?)
        """,
        (
            trace_id,
            user_id,
            query_raw,
            json.dumps(query_parsed),
            datetime.now(timezone.utc).isoformat(),
        ),
    )


def log_agent_result(
    trace_id: str,
    agent_name: str,
    input_payload: dict,
    output_payload: dict,
    latency_ms: int,
    confidence: str,
) -> None:
    """Log an individual agent invocation result."""
    execute(
        """
        INSERT INTO audit_agent_calls (
            trace_id, agent_name, input_payload,
            output_payload, latency_ms, confidence, called_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            trace_id,
            agent_name,
            json.dumps(input_payload),
            json.dumps(output_payload),
            latency_ms,
            confidence,
            datetime.now(timezone.utc).isoformat(),
        ),
    )


def log_conflict(
    trace_id: str,
    conflict_id: str,
    agent_a: str,
    agent_b: str,
    topic: str,
    resolution: str,
    winning_agent: str,
) -> None:
    """Log a detected conflict and its resolution."""
    execute(
        """
        INSERT INTO audit_conflicts (
            trace_id, conflict_id, agent_a, agent_b,
            topic, resolution, winning_agent, detected_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            trace_id,
            conflict_id,
            agent_a,
            agent_b,
            topic,
            resolution,
            winning_agent,
            datetime.now(timezone.utc).isoformat(),
        ),
    )


def log_session_complete(
    trace_id: str,
    overall_confidence: str,
    confidence_score: float,
    checkpoint_tier: str,
    output_snapshot: dict,
    total_latency_ms: int,
) -> None:
    """Update the audit record when a session completes successfully."""
    execute(
        """
        UPDATE audit_log SET
            status              = 'COMPLETED',
            overall_confidence  = ?,
            confidence_score    = ?,
            checkpoint_tier     = ?,
            output_snapshot     = ?,
            total_latency_ms    = ?,
            completed_at        = ?
        WHERE trace_id = ?
        """,
        (
            overall_confidence,
            confidence_score,
            checkpoint_tier,
            json.dumps(output_snapshot),
            total_latency_ms,
            datetime.now(timezone.utc).isoformat(),
            trace_id,
        ),
    )


def log_session_error(trace_id: str, error_message: str) -> None:
    """Update the audit record when a session fails."""
    execute(
        """
        UPDATE audit_log SET
            status       = 'FAILED',
            error_message = ?,
            completed_at = ?
        WHERE trace_id = ?
        """,
        (error_message, datetime.now(timezone.utc).isoformat(), trace_id),
    )


def log_approval(
    trace_id: str,
    approved_by: str,
    checkpoint_tier: str,
) -> None:
    """Record human sign-off on an output."""
    execute(
        """
        UPDATE audit_log SET
            approved_by   = ?,
            approved_at   = ?
        WHERE trace_id = ?
        """,
        (approved_by, datetime.now(timezone.utc).isoformat(), trace_id),
    )


# ── Query helpers ─────────────────────────────────────────────────────────────

def get_audit_record(trace_id: str) -> dict | None:
    """Retrieve the top-level audit record for a trace."""
    return query_one(
        "SELECT * FROM audit_log WHERE trace_id = ?", (trace_id,)
    )


def get_agent_calls(trace_id: str) -> list[dict]:
    """Retrieve all agent call records for a trace."""
    return query_all(
        "SELECT * FROM audit_agent_calls WHERE trace_id = ? ORDER BY called_at",
        (trace_id,),
    )


def get_conflicts(trace_id: str) -> list[dict]:
    """Retrieve all conflict records for a trace."""
    return query_all(
        "SELECT * FROM audit_conflicts WHERE trace_id = ? ORDER BY detected_at",
        (trace_id,),
    )


def get_full_audit(trace_id: str) -> dict | None:
    """Return complete audit package: session + agent calls + conflicts."""
    record = get_audit_record(trace_id)
    if not record:
        return None
    return {
        "session":     record,
        "agent_calls": get_agent_calls(trace_id),
        "conflicts":   get_conflicts(trace_id),
    }