"""
data/mock/seed_unstructured.py
───────────────────────────────
Seeds ChromaDB vector store with analyst commentary,
news articles, and research notes.
Run: python data/mock/seed_unstructured.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.vector_store import add_documents, reset_collection

# Each entry: (id, document_text, metadata)
DOCUMENTS = [
    # ── Analyst Commentary ────────────────────────────────────────────────────
    (
        "analyst-001",
        "Technology sector faced a broad sell-off in Q1 2026 driven by rising discount rates. "
        "Higher interest rates reduce the present value of future earnings, disproportionately "
        "impacting growth-oriented technology stocks. Funds with overweight positions in tech "
        "were the most severely affected, with the sector returning -2.0% in March alone.",
        {"type": "analyst_commentary", "date": "2026-03", "source": "Internal Research Desk",
         "sector": "Technology", "relevance": "performance_drag"},
    ),
    (
        "analyst-002",
        "Emerging markets underperformed significantly in Q1 2026 due to currency volatility "
        "and China growth concerns. The US Federal Reserve's hawkish stance strengthened the "
        "dollar, creating capital outflow pressure across EM economies. China's GDP growth "
        "fell to 3.7% in Q1, its weakest since 2023, driven by property sector stress and "
        "weak consumer confidence.",
        {"type": "analyst_commentary", "date": "2026-03", "source": "Internal Research Desk",
         "sector": "Emerging Markets", "relevance": "performance_drag"},
    ),
    (
        "analyst-003",
        "Investors are rotating toward defensive sectors amid macro uncertainty. Healthcare "
        "and Consumer Staples have seen the strongest inflows in 18 months as institutional "
        "allocators seek lower-beta portfolios. Funds with defensive tilts have materially "
        "outperformed growth-heavy peers across Q1 2026.",
        {"type": "analyst_commentary", "date": "2026-03", "source": "Internal Research Desk",
         "sector": "Defensive", "relevance": "peer_comparison"},
    ),
    (
        "analyst-004",
        "EMEA institutional clients have been the primary source of redemptions from global "
        "equity funds in Q1 2026. European pension funds and sovereign wealth funds are "
        "reducing global equity exposure in favour of short-duration fixed income and "
        "infrastructure assets. This trend is expected to continue through H1 2026 unless "
        "the Fed signals a pivot.",
        {"type": "analyst_commentary", "date": "2026-03", "source": "Distribution Intelligence",
         "region": "EMEA", "relevance": "fund_flows"},
    ),
    (
        "analyst-005",
        "The Global Equity Fund's (GEF001) technology overweight of 28.5% is significantly "
        "above the category average of approximately 18%. This positioning was appropriate "
        "during the 2024-2025 bull market but has become a structural drag in the current "
        "rising-rate environment. A rebalancing toward neutral or underweight tech is warranted.",
        {"type": "internal_memo", "date": "2026-04", "source": "Portfolio Strategy Team",
         "fund_id": "GEF001", "relevance": "recommendation"},
    ),

    # ── Synthetic News ────────────────────────────────────────────────────────
    (
        "news-001",
        "Federal Reserve raises rates by 25bps in March 2026 surprise move. The Federal Open "
        "Market Committee voted unanimously to raise the federal funds rate to 6.00%, citing "
        "persistent inflation above the 2% target. Markets reacted sharply with global equities "
        "falling across the board. Tech and growth stocks were hardest hit, triggering a "
        "broad risk-off rotation.",
        {"type": "news", "date": "2026-03-18", "source": "Financial Times Synthetic",
         "topic": "monetary_policy", "severity": "HIGH"},
    ),
    (
        "news-002",
        "Global equity markets see increased volatility in Q1 2026. The CBOE Volatility Index "
        "rose to its highest level since 2023 as investors grappled with persistent inflation, "
        "a hawkish Federal Reserve, and slowing growth in China. Emerging market equities were "
        "particularly affected, with the MSCI Emerging Markets index down 6.2% for the quarter.",
        {"type": "news", "date": "2026-03-31", "source": "Bloomberg Synthetic",
         "topic": "market_volatility", "severity": "MEDIUM"},
    ),
    (
        "news-003",
        "Institutional investors reduce exposure to growth-heavy portfolios in Q1 2026. "
        "A survey of 250 institutional allocators found that 68% reduced their allocation "
        "to growth equities in Q1, with the majority citing rate risk and stretched valuations. "
        "Global equity funds with high technology and EM exposure saw the largest outflows, "
        "while defensive and value-oriented funds attracted net inflows.",
        {"type": "news", "date": "2026-04-01", "source": "Reuters Synthetic",
         "topic": "institutional_flows", "severity": "MEDIUM"},
    ),
    (
        "news-004",
        "China's GDP growth slows to 3.7% in Q1 2026, missing estimates. The National Bureau "
        "of Statistics reported the weakest quarterly growth since early 2023, driven by "
        "continued property sector stress and weak domestic consumption. The data prompted "
        "further selling in emerging market equities, particularly in funds with significant "
        "China single-country exposure.",
        {"type": "news", "date": "2026-04-15", "source": "South China Morning Post Synthetic",
         "topic": "china_growth", "severity": "HIGH"},
    ),
    (
        "news-005",
        "Emerging market currencies hit three-year low against the US dollar. A basket of "
        "emerging market currencies fell to its weakest level since 2023 as the Fed rate hike "
        "drove capital back to dollar-denominated assets. Countries including Brazil, South "
        "Africa, and Indonesia saw the largest currency depreciations, creating additional "
        "headwinds for funds with unhedged EM exposure.",
        {"type": "news", "date": "2026-03-25", "source": "Wall Street Journal Synthetic",
         "topic": "em_currencies", "severity": "HIGH"},
    ),

    # ── Research Notes ────────────────────────────────────────────────────────
    (
        "research-001",
        "Q1 2026 Global Equity Fund Attribution Review — Internal Draft. "
        "Key findings: (1) Technology overweight (-0.45% contribution in March) is the primary "
        "single-sector drag. (2) EM allocation (-0.38% in March) is the second largest drag, "
        "amplified by currency effects. (3) Defensive underweights (Healthcare, Consumer Staples) "
        "created a double penalty — missed upside in the only outperforming sectors. "
        "Recommendation: Reduce tech to neutral (18-20%), increase defensive allocation.",
        {"type": "research_note", "date": "2026-04", "source": "Portfolio Analytics",
         "fund_id": "GEF001", "relevance": "root_cause"},
    ),
    (
        "research-002",
        "EMEA Distribution Review — Q1 2026. Net outflows from EMEA totalled USD 700mn "
        "in Q1, representing 6.9% of total AUM — above the 5% alert threshold. Primary "
        "redemption sources: European pension funds (40%), German insurance companies (25%), "
        "UK wealth managers (20%). Primary reason cited: risk reduction amid macro uncertainty "
        "and preference for short-duration fixed income. Engagement plan required urgently.",
        {"type": "research_note", "date": "2026-04", "source": "EMEA Distribution Team",
         "fund_id": "GEF001", "relevance": "distribution"},
    ),
]


def seed():
    reset_collection()

    ids       = [doc[0] for doc in DOCUMENTS]
    texts     = [doc[1] for doc in DOCUMENTS]
    metadatas = [doc[2] for doc in DOCUMENTS]

    add_documents(documents=texts, metadatas=metadatas, ids=ids)
    print(f"Seeded {len(DOCUMENTS)} documents into ChromaDB vector store.")


if __name__ == "__main__":
    seed()