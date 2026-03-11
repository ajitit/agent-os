"""
File: storage.py

Purpose:
Defines API endpoints for file storage operations, including uploading, downloading,
generating presigned URLs, listing, and deleting files.

Key Functionalities:
- Upload files to storage
- Download files directly
- Generate presigned URLs for secure temporary access
- List and delete files

Inputs:
- HTTP requests with file uploads / metadata
- Storage keys (file identifiers)

Outputs:
- JSON responses with file metadata and presigned URLs
- Binary streams (application/octet-stream) for file downloads

Interacting Files / Modules:
- backend.api.stores
- backend.core.exceptions
"""

from fastapi import APIRouter, File, Query, UploadFile
from fastapi.responses import Response

from backend.api.stores import storage_delete, storage_get, storage_list, storage_put
from backend.core.exceptions import NotFoundError

router = APIRouter(prefix="/storage", tags=["Storage"])


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...), key: str | None = Query(None, description="Optional storage key")
):
    """Upload a file to cloud storage."""
    k = key or file.filename or "unnamed"
    content = await file.read()
    storage_put(k, content)
    return {"key": k, "size": len(content)}


@router.get("/files/{key}")
def download_file(key: str):
    """Download a file from storage."""
    content = storage_get(key)
    if content is None:
        raise NotFoundError("File not found")
    return Response(content=content, media_type="application/octet-stream")


@router.get("/urls/{key}")
def get_presigned_url(key: str):
    """Get a presigned URL for a file."""
    if storage_get(key) is None:
        raise NotFoundError("File not found")
    return {"key": key, "url": f"/api/v1/storage/files/{key}"}


@router.delete("/files/{key}", status_code=204)
def delete_file(key: str):
    """Delete a file from storage."""
    if not storage_delete(key):
        raise NotFoundError("File not found")


@router.get("/files")
def list_files():
    """List files in storage."""
    return storage_list()
