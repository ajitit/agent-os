"""
File: manager.py

Purpose:
Orchestrates the Knowledge Management workflow.
Combines WebCrawler, DocumentProcessor, CodeExtractor, and VectorSearchEngine.
"""

<<<<<<< HEAD
from typing import Any, Optional
=======
from typing import Any
>>>>>>> c952205 (Initial upload of AgentOS code)

from backend.api import stores
from backend.knowledge.crawler import WebCrawler
from backend.knowledge.extractor import CodeExtractor
from backend.knowledge.parser import DocumentProcessor
from backend.knowledge.vector import VectorSearchEngine


class SourceManager:
    def __init__(self, vector_engine: VectorSearchEngine):
        self.crawler = WebCrawler()
        self.parser = DocumentProcessor()
        self.extractor = CodeExtractor()
        self.vector_engine = vector_engine

<<<<<<< HEAD
    def list_sources(self, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        sources = stores.source_list()
        if not filters:
            return sources
            
=======
    def list_sources(self, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        sources = stores.source_list()
        if not filters:
            return sources

>>>>>>> c952205 (Initial upload of AgentOS code)
        filtered = []
        for s in sources:
            match = True
            for k, v in filters.items():
                if k == "tags" and v:
                    if not set(v).intersection(set(s.get("tags", []))):
                        match = False
                        break
                elif s.get(k) != v:
                    match = False
                    break
            if match:
                filtered.append(s)
        return filtered

    async def add_source(self, name: str, source_type: str, url: str = None, tags: list[str] = None) -> dict:
        source_data = {
            "name": name,
            "type": source_type,
            "url": url,
            "tags": tags or [],
            "chunkCount": 0,
            "codeExampleCount": 0,
            "status": "pending"
        }
        return stores.source_create(source_data)
<<<<<<< HEAD
        
=======

>>>>>>> c952205 (Initial upload of AgentOS code)
    async def process_source(self, source_id: str, file_path: str = None):
        source = stores.source_get(source_id)
        if not source:
            raise ValueError("Source not found")
<<<<<<< HEAD
            
        stores.source_update(source_id, {"status": "processing"})
        
=======

        stores.source_update(source_id, {"status": "processing"})

>>>>>>> c952205 (Initial upload of AgentOS code)
        try:
            chunks = []
            if source["type"] == "web" and source.get("url"):
                crawl_results = await self.crawler.crawl(source["url"], source_id)
                for i, res in enumerate(crawl_results):
                    chunks.append({
                        "content": res["content"],
                        "sourceId": source_id,
                        "chunkIndex": i,
                        "metadata": {"title": res["title"], "url": res["url"]}
                    })
            elif source["type"] in ["pdf", "docx", "markdown", "txt"] and file_path:
                chunks = self.parser.process(file_path, source_id, source["type"])
            else:
                raise ValueError("Invalid source type or missing inputs")
<<<<<<< HEAD
                
            if chunks:
                self.vector_engine.upsert_chunks(chunks)
                
=======

            if chunks:
                self.vector_engine.upsert_chunks(chunks)

>>>>>>> c952205 (Initial upload of AgentOS code)
            full_text = "\n\n".join(c["content"] for c in chunks)
            code_examples = self.extractor.extract(full_text, source_id)
            for ex in code_examples:
                stores.code_example_create(ex)
<<<<<<< HEAD
                
=======

>>>>>>> c952205 (Initial upload of AgentOS code)
            stores.source_update(source_id, {
                "status": "ready",
                "chunkCount": len(chunks),
                "codeExampleCount": len(code_examples)
            })
<<<<<<< HEAD
            
=======

>>>>>>> c952205 (Initial upload of AgentOS code)
        except Exception as e:
            print(f"Error processing source {source_id}: {e}")
            stores.source_update(source_id, {"status": "error"})

    def delete_source(self, source_id: str) -> bool:
        self.vector_engine.delete_by_source(source_id)
        return stores.source_delete(source_id)
