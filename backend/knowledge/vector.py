"""
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
