"""
File: test_skills.py

Purpose:
Extensive test suite for verifying the Progressive Disclosure skill loader
functionalities.

Key Functionalities:
- Create fixtures for temporary simulated skills directories
- Verify successful listing, retrieval, and parsing of skill metadata
- Ensure resource loading works correctly
- Validate security boundaries by attempting and rejecting path traversal attacks

Inputs:
- Pytest fixtures (tmp_path)

Outputs:
- Passing or failing test assertions

Interacting Files / Modules:
- backend.skills.loader
- backend.skills.models
"""

import tempfile
from pathlib import Path

import pytest

from backend.skills.loader import SkillLoader


@pytest.fixture
def skills_dir(tmp_path: Path) -> Path:
    """Create a temporary skills directory with sample skill."""
    skill_dir = tmp_path / "sample_skill"
    skill_dir.mkdir()
    (skill_dir / "metadata.json").write_text(
        '{"name": "Sample", "description": "A sample skill", "version": "1.0.0"}',
        encoding="utf-8",
    )
    (skill_dir / "SKILL.md").write_text("# Sample Skill\n\nFull instructions.", encoding="utf-8")
    res_dir = skill_dir / "resources"
    res_dir.mkdir()
    (res_dir / "readme.txt").write_text("Resource content", encoding="utf-8")
    return tmp_path


def test_list_metadata(skills_dir: Path):
    loader = SkillLoader(skills_dir)
    skills = loader.list_metadata()
    assert len(skills) == 1
    assert skills[0].id == "sample_skill"
    assert skills[0].name == "Sample"
    assert skills[0].description == "A sample skill"


def test_get_skill(skills_dir: Path):
    loader = SkillLoader(skills_dir)
    skill = loader.get_skill("sample_skill")
    assert skill is not None
    assert skill.metadata.id == "sample_skill"
    assert "# Sample Skill" in skill.instructions
    assert "readme.txt" in skill.resource_paths


def test_get_resource(skills_dir: Path):
    loader = SkillLoader(skills_dir)
    result = loader.get_resource("sample_skill", "readme.txt")
    assert result is not None
    content, content_type = result
    assert b"Resource content" in content
    assert "text" in content_type


def test_get_nonexistent_skill(skills_dir: Path):
    loader = SkillLoader(skills_dir)
    assert loader.get_skill("nonexistent") is None


def test_path_traversal_blocked(skills_dir: Path):
    loader = SkillLoader(skills_dir)
    assert loader.get_resource("sample_skill", "../../etc/passwd") is None


def test_empty_skills_dir():
    with tempfile.TemporaryDirectory() as tmp:
        loader = SkillLoader(tmp)
        assert loader.list_metadata() == []
