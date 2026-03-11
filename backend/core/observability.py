"""
File: observability.py

Purpose:
Implements the ObservabilityService: a LangChain BaseCallbackHandler that captures
every LLM call, tool call, and chain event and persists them as spans in the store.
Also exposes helper functions consumed by the /observability API.

Key Functionalities:
- Non-blocking callback handler (fire-and-forget span writes)
- Span and run lifecycle tracking
- Structured log ingestion via logger.observe()
- Metrics snapshot aggregation
"""

from __future__ import annotations

import time
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult

from backend.api.stores import (
    metrics_snapshot,
    obs_log_append,
    run_create,
    run_get,
    run_list,
    run_update,
    span_create,
    span_list_by_run,
    span_update,
)


def _now() -> str:
    return datetime.now(UTC).isoformat()


class ObservabilityCallbackHandler(BaseCallbackHandler):
    """
    LangChain callback handler that captures execution events as spans.
    All writes are synchronous in-memory — no I/O so they won't block agents.
    """

    raise_error = False  # never let obs errors surface to callers

    def __init__(self, run_id: str, workflow_id: str, user_id: str):
        super().__init__()
        self.run_id = run_id
        self.workflow_id = workflow_id
        self.user_id = user_id
        self._span_start: dict[str, float] = {}

    # ── LLM events ──────────────────────────────────────────────────────────

    def on_llm_start(
        self,
        serialized: dict[str, Any],
        prompts: list[str],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        sid = str(run_id)
        self._span_start[sid] = time.time()
        span_create(
            {
                "spanId": sid,
                "parentSpanId": str(parent_run_id) if parent_run_id else None,
                "runId": self.run_id,
                "workflowId": self.workflow_id,
                "userId": self.user_id,
                "nodeType": "llm",
                "nodeName": serialized.get("name", "llm"),
                "startedAt": _now(),
                "input": {"prompts": prompts},
                "llmCalls": [],
                "toolCalls": [],
            }
        )

    def on_llm_end(self, response: LLMResult, *, run_id: UUID, **kwargs: Any) -> None:
        sid = str(run_id)
        elapsed = int((time.time() - self._span_start.pop(sid, time.time())) * 1000)
        generations = response.generations
        output_text = ""
        prompt_tokens = 0
        completion_tokens = 0
        if generations:
            output_text = generations[0][0].text if generations[0] else ""
        if response.llm_output:
            usage = response.llm_output.get("token_usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
        span_update(
            sid,
            {
                "endedAt": _now(),
                "durationMs": elapsed,
                "output": {"text": output_text},
                "llmCalls": [
                    {
                        "model": response.llm_output.get("model_name", "unknown") if response.llm_output else "unknown",
                        "promptTokens": prompt_tokens,
                        "completionTokens": completion_tokens,
                        "latencyMs": elapsed,
                    }
                ],
            },
        )
        # propagate tokens to run
        run = run_get(self.run_id)
        if run:
            run_update(
                self.run_id,
                {"totalTokens": run.get("totalTokens", 0) + prompt_tokens + completion_tokens},
            )

    def on_llm_error(self, error: BaseException, *, run_id: UUID, **kwargs: Any) -> None:
        sid = str(run_id)
        elapsed = int((time.time() - self._span_start.pop(sid, time.time())) * 1000)
        span_update(
            sid,
            {
                "endedAt": _now(),
                "durationMs": elapsed,
                "error": {"message": str(error)},
            },
        )
        _log(self.run_id, "error", f"LLM error: {error}")

    # ── Tool events ──────────────────────────────────────────────────────────

    def on_tool_start(
        self,
        serialized: dict[str, Any],
        input_str: str,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        sid = str(run_id)
        self._span_start[sid] = time.time()
        span_create(
            {
                "spanId": sid,
                "parentSpanId": str(parent_run_id) if parent_run_id else None,
                "runId": self.run_id,
                "workflowId": self.workflow_id,
                "userId": self.user_id,
                "nodeType": "tool",
                "nodeName": serialized.get("name", "tool"),
                "startedAt": _now(),
                "input": {"input": input_str},
                "llmCalls": [],
                "toolCalls": [],
            }
        )

    def on_tool_end(self, output: str, *, run_id: UUID, **kwargs: Any) -> None:
        sid = str(run_id)
        elapsed = int((time.time() - self._span_start.pop(sid, time.time())) * 1000)
        span_update(sid, {"endedAt": _now(), "durationMs": elapsed, "output": {"output": output}})

    def on_tool_error(self, error: BaseException, *, run_id: UUID, **kwargs: Any) -> None:
        sid = str(run_id)
        elapsed = int((time.time() - self._span_start.pop(sid, time.time())) * 1000)
        span_update(
            sid,
            {
                "endedAt": _now(),
                "durationMs": elapsed,
                "error": {"message": str(error)},
                "toolCalls": [{"name": "unknown", "success": False, "output": str(error)}],
            },
        )
        _log(self.run_id, "error", f"Tool error: {error}")

    # ── Chain events ─────────────────────────────────────────────────────────

    def on_chain_start(
        self,
        serialized: dict[str, Any],
        inputs: dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        sid = str(run_id)
        self._span_start[sid] = time.time()
        span_create(
            {
                "spanId": sid,
                "parentSpanId": str(parent_run_id) if parent_run_id else None,
                "runId": self.run_id,
                "workflowId": self.workflow_id,
                "userId": self.user_id,
                "nodeType": "chain",
                "nodeName": serialized.get("name", "chain"),
                "startedAt": _now(),
                "input": inputs,
                "llmCalls": [],
                "toolCalls": [],
            }
        )

    def on_chain_end(self, outputs: dict[str, Any], *, run_id: UUID, **kwargs: Any) -> None:
        sid = str(run_id)
        elapsed = int((time.time() - self._span_start.pop(sid, time.time())) * 1000)
        span_update(sid, {"endedAt": _now(), "durationMs": elapsed, "output": outputs})


# ── Structured log helper ────────────────────────────────────────────────────

def _log(run_id: str | None, level: str, message: str, context: dict | None = None) -> None:
    obs_log_append(
        {
            "timestamp": _now(),
            "level": level,
            "message": message,
            "runId": run_id,
            "context": context or {},
        }
    )


class ObservabilityLogger:
    """Structured logger that writes to the observability log store."""

    def __init__(self, run_id: str | None = None):
        self.run_id = run_id

    def debug(self, msg: str, **ctx: Any) -> None:
        _log(self.run_id, "debug", msg, ctx)

    def info(self, msg: str, **ctx: Any) -> None:
        _log(self.run_id, "info", msg, ctx)

    def warn(self, msg: str, **ctx: Any) -> None:
        _log(self.run_id, "warn", msg, ctx)

    def error(self, msg: str, **ctx: Any) -> None:
        _log(self.run_id, "error", msg, ctx)

    def observe(self, level: str, message: str, context: dict | None = None) -> None:
        _log(self.run_id, level, message, context)


# ── Convenience exports ──────────────────────────────────────────────────────

logger = ObservabilityLogger()

__all__ = [
    "ObservabilityCallbackHandler",
    "ObservabilityLogger",
    "logger",
    "run_create",
    "run_get",
    "run_list",
    "run_update",
    "span_list_by_run",
    "metrics_snapshot",
]
