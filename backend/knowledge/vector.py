"""
Module: knowledge/vector.py

Vector Search Engine powered by ChromaDB.  Handles embeddings, upsert, semantic
search, and optional keyword hybrid search.

ChromaDB is an optional dependency — the module guards against ``ImportError``
so the application starts cleanly in test or lightweight environments where
the heavy ML libraries are not installed.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

try:
    import chromadb  # type: ignore[import]
    from chromadb.utils import embedding_functions  # type: ignore[import]

    _CHROMADB_AVAILABLE = True
except ImportError:  # pragma: no cover
    _CHROMADB_AVAILABLE = False
    chromadb = None  # type: ignore[assignment]
    embedding_functions = None  # type: ignore[assignment]
    logger.warning(
        "chromadb not installed — VectorSearchEngine will use no-op fallback. "
        "Run 'pip install chromadb sentence-transformers' to enable vector search."
    )


class VectorSearchEngine:
    """Semantic vector search powered by ChromaDB.

    If ChromaDB is not installed the engine silently falls back to no-op
    implementations so the rest of the application continues to work.

    Args:
        persist_directory: Path for persistent ChromaDB storage.
        embedding_model: Sentence-transformers model name for embeddings.
    """

    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        embedding_model: str = "all-MiniLM-L6-v2",
    ) -> None:
        """Initialise the vector search engine.

        Args:
            persist_directory: ChromaDB storage path.
            embedding_model: Embedding model identifier.
        """
        self.persist_directory = persist_directory
        self.embedding_model = embedding_model
        self._client: Any = None
        self._collection: Any = None

        if _CHROMADB_AVAILABLE:
            try:
                self._client = chromadb.PersistentClient(path=persist_directory)
                ef = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name=embedding_model
                )
                self._collection = self._client.get_or_create_collection(
                    name="knowledge_base",
                    embedding_function=ef,
                )
                logger.info(
                    "vector_engine=ready model=%s persist=%s",
                    embedding_model,
                    persist_directory,
                )
            except Exception as exc:  # pragma: no cover
                logger.warning("vector_engine=init_failed error=%s", exc)
                self._client = None
                self._collection = None

    def upsert(
        self,
        chunk_id: str,
        text: str,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Insert or update a text chunk in the vector store.

        Args:
            chunk_id: Unique identifier for the chunk.
            text: Raw text content to embed.
            metadata: Optional metadata dict.

        Returns:
            True on success, False if the engine is unavailable.
        """
        if self._collection is None:
            return False
        try:
            self._collection.upsert(
                ids=[chunk_id],
                documents=[text],
                metadatas=[metadata or {}],
            )
            return True
        except Exception as exc:
            logger.error("vector_engine=upsert_failed id=%s error=%s", chunk_id, exc)
            return False

    def search(
        self,
        query: str,
        n_results: int = 5,
        where: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Perform semantic similarity search.

        Args:
            query: Query text.
            n_results: Number of results to return.
            where: Optional ChromaDB ``where`` filter clause.

        Returns:
            List of result dicts with keys ``id``, ``text``, ``distance``, ``metadata``.
        """
        if self._collection is None:
            return []
        try:
            kwargs: dict[str, Any] = {"query_texts": [query], "n_results": n_results}
            if where:
                kwargs["where"] = where
            raw = self._collection.query(**kwargs)
            results: list[dict[str, Any]] = []
            ids = (raw.get("ids") or [[]])[0]
            docs = (raw.get("documents") or [[]])[0]
            distances = (raw.get("distances") or [[]])[0]
            metadatas = (raw.get("metadatas") or [[]])[0]
            for i, doc_id in enumerate(ids):
                results.append({
                    "id": doc_id,
                    "text": docs[i] if i < len(docs) else "",
                    "distance": distances[i] if i < len(distances) else 1.0,
                    "metadata": metadatas[i] if i < len(metadatas) else {},
                })
            return results
        except Exception as exc:
            logger.error("vector_engine=search_failed error=%s", exc)
            return []

    def delete(self, chunk_id: str) -> bool:
        """Delete a chunk from the vector store.

        Args:
            chunk_id: Chunk identifier to remove.

        Returns:
            True on success, False if unavailable or error.
        """
        if self._collection is None:
            return False
        try:
            self._collection.delete(ids=[chunk_id])
            return True
        except Exception as exc:
            logger.error("vector_engine=delete_failed id=%s error=%s", chunk_id, exc)
            return False

    def delete_by_source(self, source_id: str) -> bool:
        """Delete all chunks belonging to a given source.

        Args:
            source_id: Source identifier whose chunks should be removed.

        Returns:
            True on success, False if unavailable or error.
        """
        if self._collection is None:
            return False
        try:
            self._collection.delete(where={"sourceId": source_id})
            return True
        except Exception as exc:
            logger.error("vector_engine=delete_by_source_failed source=%s error=%s", source_id, exc)
            return False


    @property
    def available(self) -> bool:
        """Return True if the vector engine is operational.

        Returns:
            Availability boolean.
        """
        return self._collection is not None
