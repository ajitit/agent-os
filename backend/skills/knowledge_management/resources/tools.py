"""
Agent Tools for Knowledge Management.
Integrates with the VectorSearchEngine and SourceManager.
"""

from backend.api.knowledge import manager, vector_engine


async def knowledge_search(query: str, top_k: int = 5, doc_type: str = None) -> list[dict]:
    """
    Search the knowledge base for factual information, code examples, or documentation.

    Args:
        query: The search query string.
        top_k: Number of most relevant results to return (default 5).
        doc_type: Optional filter (e.g. 'web', 'pdf', 'docx', 'markdown', 'txt').

    Returns:
        List of dictionaries containing matched text chunks, scores, and metadata.
    """
    filters = {"type": doc_type} if doc_type else None
    results = vector_engine.search(query=query, top_k=top_k, filters=filters)
    return results


async def knowledge_ingest(name: str, source_type: str, url: str = None, file_path: str = None) -> dict:
    """
    Ingest a new knowledge source into the system.

    Args:
        name: A human-readable name for the source.
        source_type: One of 'web', 'pdf', 'docx', 'markdown', or 'txt'.
        url: The URL to crawl (if source_type corresponds to 'web').
        file_path: The local file path (if source_type corresponds to a document).

    Returns:
        Status dictionary reflecting the progress.
    """
    # Create the source record
    source = await manager.add_source(name=name, source_type=source_type, url=url)
    source_id = source["id"]

    # Process synchronously within the tool call so the agent knows it completed
    await manager.process_source(source_id=source_id, file_path=file_path)

    return {
        "status": "success",
        "message": f"Source '{name}' successfully ingested.",
        "source_id": source_id
    }


async def knowledge_list_sources(source_type: str = None) -> list[dict]:
    """
    List currently ingested knowledge sources.

    Args:
        source_type: Optional string to filter by type ('web', 'pdf', 'docx', etc.)

    Returns:
        List of source metadata dictionaries (id, name, type, chunkCount, status, etc.)
    """
    filters = {"type": source_type} if source_type else None
    return manager.list_sources(filters=filters)
