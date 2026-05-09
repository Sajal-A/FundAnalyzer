"""
main.py
────────
Application entry point.

Usage:
    python main.py               # Start the API server
    python main.py --seed        # Seed all mock data then start
    python main.py --seed-only   # Seed only (no server)
"""

import sys
import argparse
from pathlib import Path

# ── Logging setup ─────────────────────────────────────────────────────────────
from loguru import logger
from core.config import settings

Path("logs").mkdir(exist_ok=True)
logger.add(settings.log_file, rotation="10 MB", retention="30 days", level=settings.log_level)
logger.add(sys.stdout, level=settings.log_level, colorize=True)


def run_seed():
    from data.mock.seed_all import seed_all
    seed_all()


def run_server():
    import uvicorn
    logger.info("Starting Fund Performance Diagnostic AI server...")
    uvicorn.run(
        "api.main:app",
        host    = "0.0.0.0",
        port    = 8000,
        reload  = True,
        log_level = settings.log_level.lower(),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fund Performance Diagnostic AI")
    parser.add_argument("--seed",      action="store_true", help="Seed mock data before starting")
    parser.add_argument("--seed-only", action="store_true", help="Seed mock data and exit")
    args = parser.parse_args()

    if args.seed_only:
        run_seed()
        sys.exit(0)

    if args.seed:
        run_seed()

    run_server()