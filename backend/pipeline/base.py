"""
Pipeline base — abstract Stage interface and StageRegistry.

All nine pipeline stages implement :class:`BaseStage`.  The
:class:`StageRegistry` resolves stages by name so the orchestrator
can build arbitrary pipelines from configuration without importing
stage modules directly.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import ClassVar

from backend.pipeline.models import PipelineContext

logger = logging.getLogger(__name__)


class BaseStage(ABC):
    """Abstract base class for every pipeline stage.

    Subclasses must implement :meth:`process`, which receives the current
    :class:`~backend.pipeline.models.PipelineContext`, performs its work,
    and returns a (potentially enriched) context.

    Class Attributes:
        stage_name: Unique identifier used by the registry.
    """

    stage_name: ClassVar[str]

    @abstractmethod
    async def process(self, ctx: PipelineContext) -> PipelineContext:
        """Execute this stage and return an updated context.

        Args:
            ctx: The current pipeline context.

        Returns:
            A new PipelineContext (or the same instance) with this stage's
            results populated.

        Raises:
            Exception: Any unhandled exception will be caught by the
                orchestrator and recorded in ``ctx.stage_errors``.
        """

    async def safe_process(self, ctx: PipelineContext) -> PipelineContext:
        """Wrap :meth:`process` with structured logging and error capture.

        Args:
            ctx: Current pipeline context.

        Returns:
            Updated context. On failure, the stage error is recorded in
            ``ctx.stage_errors`` and the original context is returned so
            the pipeline can continue.
        """
        logger.info(
            "stage=start name=%s run_id=%s",
            self.stage_name,
            ctx.run_id,
        )
        try:
            result = await self.process(ctx)
            logger.info(
                "stage=end name=%s run_id=%s",
                self.stage_name,
                ctx.run_id,
            )
            return result
        except Exception as exc:
            logger.exception(
                "stage=error name=%s run_id=%s error=%s",
                self.stage_name,
                ctx.run_id,
                exc,
            )
            errors = {**ctx.stage_errors, self.stage_name: str(exc)}
            return ctx.with_update(stage_errors=errors)


class StageRegistry:
    """Registry mapping stage names to :class:`BaseStage` instances.

    Stages are registered once at application start-up; the orchestrator
    resolves them by name at runtime.
    """

    def __init__(self) -> None:
        self._stages: dict[str, BaseStage] = {}

    def register(self, stage: BaseStage) -> None:
        """Register a stage instance.

        Args:
            stage: Stage instance to register.

        Raises:
            ValueError: If a stage with the same name is already registered.
        """
        name = stage.stage_name
        if name in self._stages:
            raise ValueError(f"Stage '{name}' is already registered.")
        self._stages[name] = stage
        logger.debug("pipeline registry=register stage=%s", name)

    def get(self, name: str) -> BaseStage:
        """Retrieve a registered stage by name.

        Args:
            name: Stage name as defined by ``BaseStage.stage_name``.

        Returns:
            The registered stage instance.

        Raises:
            KeyError: If no stage with the given name is registered.
        """
        if name not in self._stages:
            raise KeyError(f"Stage '{name}' is not registered.")
        return self._stages[name]

    def list_names(self) -> list[str]:
        """Return all registered stage names in insertion order.

        Returns:
            List of stage name strings.
        """
        return list(self._stages.keys())
