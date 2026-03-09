from fastapi import FastAPI
from backend.api import agents, tasks, chat

app = FastAPI(title="AgentOS")

app.include_router(agents.router)
app.include_router(tasks.router)
app.include_router(chat.router)

@app.get("/")
def root():
    return {"status": "AgentOS running"}
