"""
<<<<<<< HEAD
File: vector.py

Purpose:
Vector Search Engine powered by ChromaDB. Handles embeddings, upserting chunks,
semantic and optional keyword hybrid search, re-ranking, and filtering.
"""

import os
from typing import Any, Optional

import chromadb
from chromadb.utils import embedding_functions


class VectorSearchEngine:
    def __init__(self, persist_directory: str = "./chroma_db", embedding_model: str = "all-MiniLM-L6-v2"):
        self.persist_directory = persist_directory
        # For development, we use Chroma's PersistentClient.
        # It automatically uses the default sentence-transformers model.
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=embedding_model)
        
        self.collection = self.client.get_or_create_collection(
            name="knowledge_chunks",
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )

    def upsert_chunks(self, chunks: list[dict[str, Any]]):
        if not chunks:
            return
            
        ids = []
        documents = []
        metadatas = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{chunk['sourceId']}_{chunk.get('chunkIndex', i)}"
            ids.append(chunk_id)
            documents.append(chunk["content"])
            
            # Clean metadata (Chroma expects string, int, float or bool)
            meta = chunk.get("metadata", {}).copy()
            meta["sourceId"] = chunk["sourceId"]
            meta["chunkIndex"] = chunk.get("chunkIndex", i)
            
            # Ensure safe types
            safe_meta = {}
            for k, v in meta.items():
                if isinstance(v, (str, int, float, bool)):
                    safe_meta[k] = v
                elif v is not None:
                    safe_meta[k] = str(v)
            metadatas.append(safe_meta)
            
        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

    def delete_by_source(self, source_id: str):
        self.collection.delete(
            where={"sourceId": source_id}
        )

    def search(
        self, 
        query: str, 
        top_k: int = 5, 
        filters: Optional[dict[str, Any]] = None,
        semantic_weight: float = 0.7
    ) -> list[dict[str, Any]]:
        where_clause = filters if filters else None
        
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k * 2, # Fetch more for re-ranking / hybrid
            where=where_clause,
            include=["documents", "metadatas", "distances"]
        )
        
        if not results["ids"] or not results["ids"][0]:
            return []
            
        # Parse results
        parsed = []
        doc_ids = results["ids"][0]
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        distances = results["distances"][0]
        
        # Lower distance is better for cosine in Chroma -> convert to similarity score
        for i in range(len(doc_ids)):
            semantic_score = 1.0 - distances[i]
            
            # Simple keyword matching as fallback "BM25" approximation
            keyword_score = self._simple_keyword_score(query, docs[i])
            
            # Hybrid score
            final_score = (semantic_score * semantic_weight) + (keyword_score * (1.0 - semantic_weight))
            
            parsed.append({
                "chunkId": doc_ids[i],
                "content": docs[i],
                "score": final_score,
                "metadata": metas[i]
            })
            
        # Sort by hybrid score and take top_k
        parsed.sort(key=lambda x: x["score"], reverse=True)
        return parsed[:top_k]

    def _simple_keyword_score(self, query: str, document: str) -> float:
        # A basic Jaccard / frequency overlap approximation for standalone keyword score.
        query_terms = set(query.lower().split())
        doc_terms = document.lower().split()
        if not query_terms or not doc_terms:
            return 0.0
            
        matches = sum(1 for term in doc_terms if term in query_terms)
        return min(matches / len(query_terms), 1.0)
=======
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

    @property
    def available(self) -> bool:
        """Return True if the vector engine is operational.

        Returns:
            Availability boolean.
        """
        return self._collection is not None
>>>>>>> c952205 (Initial upload of AgentOS code)
