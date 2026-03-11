"""
Package: backend.api

Exports all FastAPI router modules for registration in the main application factory.

New routers added in this version:
- audit: Immutable audit log query and export
- plans: Supervisor plan CRUD with task management
- marketplace: Skill / Model / Tool registry
"""

__all__ = [
    "agents",
    "audit",
    "auth",
    "chat",
    "conversations",
    "crews",
    "health",
    "knowledge",
    "llm",
    "marketplace",
    "mcp_servers",
    "observability",
    "pipeline",
    "plans",
    "preferences",
    "settings",
    "skills",
    "storage",
    "supervisor",
    "tasks",
    "workflows",
]
