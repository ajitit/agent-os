"""
Skill loader - Progressive Disclosure implementation.

Level 1: Metadata only (~100 tokens) - for system prompt
Level 2: Full instructions (SKILL.md) - loaded when agent selects skill
Level 3: Resources - loaded when instructions reference them
"""

import json
from pathlib import Path
from typing import Any

from backend.skills.models import Skill, SkillMetadata


class SkillLoader:
    """
    Framework-agnostic skill loader.
    Works with any AI framework - returns plain data structures.
    """

    def __init__(self, base_dir: str | Path) -> None:
        self.base_dir = Path(base_dir).resolve()

    def _skill_path(self, skill_id: str) -> Path:
        """Resolve skill directory, preventing path traversal."""
        path = (self.base_dir / skill_id).resolve()
        if not str(path).startswith(str(self.base_dir)):
            raise ValueError("Invalid skill id")
        return path

    def list_metadata(self) -> list[SkillMetadata]:
        """
        Level 1: Load metadata for all skills.
        ~100 tokens per skill - use in system prompt.
        """
        result: list[SkillMetadata] = []
        if not self.base_dir.exists():
            return result

        for path in self.base_dir.iterdir():
            if path.is_dir():
                meta_file = path / "metadata.json"
                if meta_file.exists():
                    try:
                        data = json.loads(meta_file.read_text(encoding="utf-8"))
                        data["id"] = path.name
                        result.append(SkillMetadata.model_validate(data))
                    except Exception:
                        continue
        return result

    def get_metadata(self, skill_id: str) -> SkillMetadata | None:
        """Level 1: Get metadata for a single skill."""
        path = self._skill_path(skill_id)
        meta_file = path / "metadata.json"
        if not meta_file.exists():
            return None
        data = json.loads(meta_file.read_text(encoding="utf-8"))
        data["id"] = skill_id
        return SkillMetadata.model_validate(data)

    def get_skill(self, skill_id: str) -> Skill | None:
        """
        Level 2: Load full skill with instructions.
        Call when agent chooses to use the skill.
        """
        metadata = self.get_metadata(skill_id)
        if not metadata:
            return None

        path = self._skill_path(skill_id)
        skill_md = path / "SKILL.md"
        instructions = ""
        if skill_md.exists():
            instructions = skill_md.read_text(encoding="utf-8")

        resources_dir = path / "resources"
        resource_paths: list[str] = []
        if resources_dir.exists():
            for r in resources_dir.rglob("*"):
                if r.is_file():
                    resource_paths.append(str(r.relative_to(resources_dir)).replace("\\", "/"))

        return Skill(
            metadata=metadata,
            instructions=instructions,
            resource_paths=resource_paths,
        )

    def get_resource(self, skill_id: str, resource_path: str) -> tuple[bytes, str] | None:
        """
        Level 3: Load a specific resource file.
        Call when instructions reference a resource.
        """
        if ".." in resource_path or resource_path.startswith("/"):
            return None

        path = self._skill_path(skill_id) / "resources" / resource_path
        path = path.resolve()
        resources_dir = (self._skill_path(skill_id) / "resources").resolve()
        if not str(path).startswith(str(resources_dir)) or not path.exists() or not path.is_file():
            return None

        content = path.read_bytes()
        suffix = path.suffix.lower()
        content_type = {
            ".md": "text/markdown",
            ".txt": "text/plain",
            ".json": "application/json",
            ".py": "text/x-python",
        }.get(suffix, "application/octet-stream")
        return (content, content_type)
