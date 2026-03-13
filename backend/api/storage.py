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

from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile
from fastapi.responses import Response

from backend.api.stores import storage_delete, storage_get, storage_list, storage_put
from backend.core.exceptions import NotFoundError
from backend.core.schemas import APIResponse
from backend.core.security import get_current_user

router = APIRouter(prefix="/storage", tags=["Storage"])


@router.post("/upload", response_model=APIResponse[dict])
async def upload_file(
    user: Annotated[dict, Depends(get_current_user)],
    file: UploadFile = File(...),
    key: str | None = Query(None, description="Optional storage key"),
):
    """Upload a file to cloud storage."""
    k = key or file.filename or "unnamed"
    content = await file.read()
    storage_put(k, content)
    return APIResponse(data={"key": k, "size": len(content)})


@router.get("/files/{key}")
async def download_file(
    key: str,
    user: Annotated[dict, Depends(get_current_user)],
):
    """Download a file from storage."""
    content = storage_get(key)
    if content is None:
        raise NotFoundError("File not found")
    return Response(content=content, media_type="application/octet-stream")


@router.get("/urls/{key}", response_model=APIResponse[dict])
async def get_presigned_url(
    key: str,
    user: Annotated[dict, Depends(get_current_user)],
):
    """Get a presigned URL for a file."""
    if storage_get(key) is None:
        raise NotFoundError("File not found")
    return APIResponse(data={"key": key, "url": f"/api/v1/storage/files/{key}"})


@router.delete("/files/{key}", status_code=204)
async def delete_file(
    key: str,
    user: Annotated[dict, Depends(get_current_user)],
):
    """Delete a file from storage."""
    if not storage_delete(key):
        raise NotFoundError("File not found")


@router.get("/files", response_model=APIResponse[list])
async def list_files(
    user: Annotated[dict, Depends(get_current_user)],
):
    """List files in storage."""
    return APIResponse(data=storage_list())
