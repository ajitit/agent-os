"""
File: __init__.py

Purpose:
Marks the backend.skills directory as a Python package and exports key models
and loaders for the Progressive Disclosure skill system.

Key Functionalities:
- Export `SkillLoader`, `Skill`, `SkillMetadata`, `SkillResource`

Inputs:
- None

Outputs:
- None

Interacting Files / Modules:
- backend.skills.loader
- backend.skills.models
"""

from backend.skills.loader import SkillLoader
from backend.skills.models import Skill, SkillMetadata, SkillResource

__all__ = ["SkillLoader", "Skill", "SkillMetadata", "SkillResource"]
