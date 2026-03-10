"""Storage API - file upload, download, presigned URLs, list, delete."""

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
