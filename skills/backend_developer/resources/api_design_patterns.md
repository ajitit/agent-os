# Vishwakarma API Design Patterns

## Standard CRUD Route Module
```python
# backend/api/{resource}s.py
from fastapi import APIRouter
from backend.core.schemas import APIResponse
from backend.core.exceptions import AgentOSException
from backend.api.stores import _resources
from pydantic import BaseModel
from uuid import uuid4

router = APIRouter(prefix="/resources", tags=["resources"])

class ResourceCreate(BaseModel):
    name: str
    description: str

class ResourceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

@router.post("", response_model=APIResponse[dict])
async def create_resource(payload: ResourceCreate, request: Request):
    resource_id = str(uuid4())
    resource = {"id": resource_id, **payload.model_dump(), "status": "active"}
    _resources[resource_id] = resource
    return APIResponse(data=resource)

@router.get("", response_model=APIResponse[list[dict]])
async def list_resources():
    return APIResponse(data=list(_resources.values()))

@router.get("/{resource_id}", response_model=APIResponse[dict])
async def get_resource(resource_id: str):
    if resource_id not in _resources:
        raise AgentOSException(status_code=404, detail="Resource not found")
    return APIResponse(data=_resources[resource_id])
```

## Response Envelope
```python
from backend.core.schemas import APIResponse, ResponseMeta
# Always wrap: APIResponse(data=payload)
# Never return raw dicts from route handlers
```

## Error Handling
```python
from backend.core.exceptions import AgentOSException
raise AgentOSException(status_code=404, detail="Agent not found")
raise AgentOSException(status_code=409, detail="Name already exists")
# 422 Validation errors handled automatically by FastAPI/Pydantic
```

## Router Registration (app/main.py)
```python
from backend.api import my_resource
app.include_router(my_resource.router, prefix=settings.api_v1_prefix)
```
