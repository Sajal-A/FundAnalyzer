"""
core/vector_store.py
────────────────────
ChromaDB client — runs fully in-process (no server required).
Persists to disk at the path defined in settings.
"""

from functools import lru_cache
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings

from core.config import settings
from core.exceptions import VectorStoreError


@lru_cache()
def get_chroma_client() -> chromadb.PersistentClient:
    """Singleton ChromaDB client — persistent, in-process."""
    Path(settings.chroma_path).mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(
        path=settings.chroma_path,
        settings=ChromaSettings(anonymized_telemetry=False),
    )


def get_collection() -> chromadb.Collection:
    """Returns (or creates) the main fund insights collection."""
    client = get_chroma_client()
    try:
        return client.get_or_create_collection(
            name=settings.chroma_collection,
            metadata={"hnsw:space": "cosine"},
        )
    except Exception as e:
        raise VectorStoreError(f"Failed to get ChromaDB collection: {e}") from e


def search_documents(
    query: str,
    n_results: int = 5,
    where: dict | None = None,
) -> list[dict]:
    """
    Semantic search in the vector store.

    Returns a list of dicts:
        {
            "id":        str,
            "document":  str,
            "metadata":  dict,
            "distance":  float,   # cosine distance (lower = more similar)
            "similarity": float,  # 1 - distance
        }
    """
    collection = get_collection()
    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"],
        )
        output = []
        for i, doc_id in enumerate(results["ids"][0]):
            distance = results["distances"][0][i]
            output.append({
                "id":         doc_id,
                "document":   results["documents"][0][i],
                "metadata":   results["metadatas"][0][i],
                "distance":   distance,
                "similarity": round(1 - distance, 4),
            })
        return output
    except Exception as e:
        raise VectorStoreError(f"Search failed: {e}") from e


def add_documents(
    documents: list[str],
    metadatas: list[dict],
    ids: list[str],
) -> None:
    """Insert documents into the vector store."""
    collection = get_collection()
    try:
        collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
    except Exception as e:
        raise VectorStoreError(f"Failed to insert documents: {e}") from e


def reset_collection() -> None:
    """Drop and recreate the collection (useful for re-seeding)."""
    client = get_chroma_client()
    try:
        client.delete_collection(settings.chroma_collection)
    except Exception:
        pass  # Collection may not exist yet
    get_collection()