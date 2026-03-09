from fastapi import APIRouter

router = APIRouter(prefix="/agents")

@router.get("/")
def list_agents():
    return [{"name":"research-agent"},{"name":"coding-agent"}]
