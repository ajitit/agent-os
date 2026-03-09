from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/tasks")

class TaskRequest(BaseModel):
    goal: str

@router.post("/")
def create_task(req: TaskRequest):
    return {"goal": req.goal, "status":"queued"}
