"""
tools/vector_tools.py
──────────────────────
Strands @tool functions for ChromaDB semantic search (RAG).
Used by the Market Intelligence Agent to retrieve
analyst commentary and news context.
"""

from strands import tool
from core.vector_store import search_documents
from core.config import settings


@tool
def search_analyst_commentary(query: str, n_results: int = 4) -> list[dict]:
    """
    Semantic search across analyst reports and internal research memos
    to find relevant commentary for a given topic.

    Args:
        query:     Natural language query (e.g. 'technology sector sell-off reasons')
        n_results: Maximum number of documents to return (default 4)

    Returns:
        List of matching documents with text, metadata,
        and similarity score. Only returns results above
        the configured similarity threshold.
    """
    results = search_documents(
        query=query,
        n_results=n_results,
        where={"type": {"$in": ["analyst_commentary", "internal_memo", "research_note"]}},
    )
    return [
        r for r in results
        if r["similarity"] >= settings.vector_similarity_threshold
    ]


@tool
def search_news_sentiment(query: str, n_results: int = 3) -> list[dict]:
    """
    Semantic search across synthetic news articles to find
    market sentiment and recent event context.

    Args:
        query:     Natural language query (e.g. 'Federal Reserve rate hike impact')
        n_results: Maximum number of news articles to return (default 3)

    Returns:
        List of relevant news articles with text, metadata,
        and similarity score above threshold.
    """
    results = search_documents(
        query=query,
        n_results=n_results,
        where={"type": {"$in": ["news"]}},
    )
    return [
        r for r in results
        if r["similarity"] >= settings.vector_similarity_threshold
    ]


@tool
def search_all_documents(query: str, n_results: int = 5) -> list[dict]:
    """
    Broad semantic search across ALL document types
    (analyst commentary, news, research notes, internal memos).
    Use when you want the most relevant context regardless of source type.

    Args:
        query:     Natural language query
        n_results: Maximum number of results (default 5)

    Returns:
        List of most relevant documents above similarity threshold,
        ordered by similarity score descending.
    """
    results = search_documents(query=query, n_results=n_results)
    filtered = [
        r for r in results
        if r["similarity"] >= settings.vector_similarity_threshold
    ]
    return sorted(filtered, key=lambda x: x["similarity"], reverse=True)