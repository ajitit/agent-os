"""
File: knowledge.py

Purpose:
FastAPI router for the Knowledge Management module. Exposes endpoints
for source management and vector search.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from backend.knowledge.manager import SourceManager
from backend.knowledge.vector import VectorSearchEngine

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

vector_engine = VectorSearchEngine()
manager = SourceManager(vector_engine)

class SourceCreateItem(BaseModel):
    name: str
    type: str
    url: Optional[str] = None
    tags: Optional[List[str]] = []
    
class SearchQuery(BaseModel):
    query: str
    top_k: int = 5
    filters: Optional[Dict[str, Any]] = None

@router.post("/sources")
async def create_source(item: SourceCreateItem, background_tasks: BackgroundTasks):
    source = await manager.add_source(
        name=item.name, 
        source_type=item.type, 
        url=item.url, 
        tags=item.tags
    )
    if item.url:
        background_tasks.add_task(manager.process_source, source["id"])
    return source

@router.get("/sources")
def list_sources(type: Optional[str] = None):
    filters = {}
    if type:
        filters["type"] = type
    return manager.list_sources(filters)

@router.delete("/sources/{source_id}")
def delete_source(source_id: str):
    success = manager.delete_source(source_id)
    if not success:
        raise HTTPException(status_code=404, detail="Source not found")
    return {"status": "deleted"}

@router.post("/sources/{source_id}/refresh")
async def refresh_source(source_id: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(manager.process_source, source_id)
    return {"status": "refreshing"}

@router.post("/search")
def search_knowledge(query: SearchQuery):
    results = vector_engine.search(
        query=query.query, 
        top_k=query.top_k, 
        filters=query.filters
    )
    return {"results": results}
