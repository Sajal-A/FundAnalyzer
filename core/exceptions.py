"""
core/exceptions.py
──────────────────
Custom exception hierarchy for the system.
"""


class FundDiagnosticError(Exception):
    """Base exception for all system errors."""


class DatabaseError(FundDiagnosticError):
    """Raised on SQLite failures."""


class VectorStoreError(FundDiagnosticError):
    """Raised on ChromaDB failures."""


class AgentError(FundDiagnosticError):
    """Raised when an agent fails to produce a valid output."""


class OrchestratorError(FundDiagnosticError):
    """Raised when orchestration fails."""


class MandateViolationError(FundDiagnosticError):
    """Raised when a recommendation violates the fund mandate."""


class DataNotFoundError(FundDiagnosticError):
    """Raised when expected data is missing from the database."""


class ConfigurationError(FundDiagnosticError):
    """Raised on missing or invalid configuration."""