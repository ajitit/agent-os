from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/chat")

async def stream():
    yield "Agent thinking...\n"
    yield "Done."

@router.get("/stream")
async def chat_stream():
    return StreamingResponse(stream())
