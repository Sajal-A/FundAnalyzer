"""
core/confidence.py
──────────────────
Confidence scoring engine.
Computes an objective confidence score from 5 weighted factors.
Returns a ConfidenceResult with level (HIGH/MEDIUM/LOW), numeric score, and reason.
"""

from dataclasses import dataclass, field

from core.config import settings


@dataclass
class ConfidenceResult:
    level:  str           # "HIGH" | "MEDIUM" | "LOW"
    score:  float         # 0.0 → 1.0
    reason: str           # Human-readable explanation
    factors: dict = field(default_factory=dict)


def compute_confidence(
    data_completeness: float        = 1.0,  # 0–1: fraction of expected records present
    inter_agent_consistency: float  = 1.0,  # 0–1: 1 = full agreement, 0 = full conflict
    data_freshness: float           = 1.0,  # 0–1: 1 = current, 0 = stale
    source_trust_tier: float        = 1.0,  # 0–1: Tier1=1.0, Tier2=0.8, Tier3=0.6, Tier4=0.3
    vector_similarity: float        = 1.0,  # 0–1: RAG similarity score (1.0 if unused)
) -> ConfidenceResult:
    """
    Weighted confidence calculation:
        data_completeness       30%
        inter_agent_consistency 25%
        data_freshness          20%
        source_trust_tier       15%
        vector_similarity       10%
    """
    weights = {
        "data_completeness":       0.30,
        "inter_agent_consistency": 0.25,
        "data_freshness":          0.20,
        "source_trust_tier":       0.15,
        "vector_similarity":       0.10,
    }

    inputs = {
        "data_completeness":       data_completeness,
        "inter_agent_consistency": inter_agent_consistency,
        "data_freshness":          data_freshness,
        "source_trust_tier":       source_trust_tier,
        "vector_similarity":       vector_similarity,
    }

    score = sum(weights[k] * inputs[k] for k in weights)
    score = round(min(max(score, 0.0), 1.0), 4)

    # Map score to level
    if score >= settings.confidence_threshold_high:
        level = "HIGH"
    elif score >= settings.confidence_threshold_medium:
        level = "MEDIUM"
    else:
        level = "LOW"

    # Build human-readable reason
    issues = []
    if data_completeness < 0.8:
        issues.append(f"data completeness low ({data_completeness:.0%})")
    if inter_agent_consistency < 0.7:
        issues.append("inter-agent conflicts detected")
    if data_freshness < 0.7:
        issues.append("data may be stale")
    if source_trust_tier < 0.6:
        issues.append("relying on lower-trust data sources")
    if vector_similarity < settings.vector_similarity_threshold:
        issues.append(f"RAG similarity below threshold ({vector_similarity:.2f})")

    if not issues:
        reason = "All signals aligned; full data available; no conflicts detected."
    else:
        reason = "Confidence reduced due to: " + "; ".join(issues) + "."

    return ConfidenceResult(
        level=level,
        score=score,
        reason=reason,
        factors={k: round(v, 4) for k, v in inputs.items()},
    )


def source_tier_score(tier: int) -> float:
    """Convert a source tier (1–4) to a 0–1 score."""
    return {1: 1.0, 2: 0.80, 3: 0.60, 4: 0.30}.get(tier, 0.30)


def checkpoint_tier(confidence_level: str, is_recommendation: bool, impact_pct: float = 0.0) -> str:
    """
    Determine the human checkpoint tier for a finding or recommendation.

    GREEN  — auto-cleared
    AMBER  — advisor review required
    RED    — blocked until analyst sign-off
    """
    if confidence_level == "LOW":
        return "RED"
    if is_recommendation:
        if impact_pct >= 10.0 or confidence_level == "LOW":
            return "RED"
        return "AMBER"
    # Factual findings
    if confidence_level == "HIGH":
        return "GREEN"
    return "AMBER"