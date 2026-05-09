"""
data/mock/seed_all.py
──────────────────────
Master seed script — runs all individual seed scripts in order.
Run once to fully initialize the local database and vector store.

Usage:
    python data/mock/seed_all.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from loguru import logger
from data.schema.init_db import init_db
from data.mock.fund_performance import seed as seed_performance
from data.mock.sector_attribution import seed as seed_sectors
from data.mock.aum_flow import seed as seed_flows
from data.mock.market_intelligence import seed as seed_market
from data.mock.competitor import seed as seed_competitors
from data.mock.unstructured import seed as seed_unstructured


def seed_all():
    logger.info("=" * 60)
    logger.info("Fund Diagnostic AI — Full Data Seed")
    logger.info("=" * 60)

    logger.info("[1/7] Initializing database schema...")
    init_db()

    logger.info("[2/7] Seeding fund performance data...")
    seed_performance()

    logger.info("[3/7] Seeding sector & geographic attribution...")
    seed_sectors()

    logger.info("[4/7] Seeding AUM & fund flows...")
    seed_flows()

    logger.info("[5/7] Seeding market intelligence...")
    seed_market()

    logger.info("[6/7] Seeding competitor / peer funds...")
    seed_competitors()

    logger.info("[7/7] Seeding unstructured docs into ChromaDB...")
    seed_unstructured()

    logger.success("=" * 60)
    logger.success("All seed data loaded successfully.")
    logger.success("You can now run: uvicorn api.main:app --reload")
    logger.success("=" * 60)


if __name__ == "__main__":
    seed_all()