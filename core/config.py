"""
core/config.py
──────────────
Central configuration — reads from .env via pydantic-settings.
All other modules import from here; never read os.environ directly.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── LLM ───────────────────────────────────────────────────────────────────
    OPENAI_API_KEY: str = "openai_api_key"
    openai_model: str = "gpt-4o"
    openai_max_tokens: int = 4096
    openai_temperature: float = 0.1

    # ── Database ──────────────────────────────────────────────────────────────
    db_path: str = "./fund_diagnostic.db"

    # ── Vector Store ──────────────────────────────────────────────────────────
    chroma_path: str = "./vector_store"
    chroma_collection: str = "fund_insights"

    # ── Logging ───────────────────────────────────────────────────────────────
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"

    # ── Confidence Thresholds ─────────────────────────────────────────────────
    confidence_threshold_high: float = 0.80
    confidence_threshold_medium: float = 0.55

    # ── Audit ─────────────────────────────────────────────────────────────────
    audit_retention_days: int = 365
    enable_show_your_work: bool = True

    # ── Agent Behaviour ───────────────────────────────────────────────────────
    agent_timeout_seconds: int = 120
    vector_similarity_threshold: float = 0.75

    # ── Fund Metadata (business rules) ───────────────────────────────────────
    underperformance_threshold_bps: float = -50.0  # fund_return < benchmark - 50bps
    underperformance_consecutive_months: int = 2
    outflow_alert_threshold_pct: float = 5.0       # > 5% of AUM in a quarter
    peer_category: str = "Global Large Cap Equity"
    default_fund_id: str = "GEF001"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings — call this everywhere instead of instantiating directly."""
    return Settings()


# Convenience alias
settings = get_settings()