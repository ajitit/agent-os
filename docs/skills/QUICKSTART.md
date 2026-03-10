# Skills - Progressive Disclosure Quick Start

## What is Progressive Disclosure?

Progressive disclosure manages AI context efficiently. Instead of loading everything into the system prompt, skills are loaded in three levels:

| Level | Content | When Loaded |
| ----- | ------- | ----------- |
| **1. Metadata** | ~100 tokens per skill (name, description) | System prompt – agent chooses relevant skill |
| **2. Instructions** | Full `SKILL.md` | When agent decides to use the skill |
| **3. Resources** | Files in `resources/` | When instructions reference them |

This allows hundreds of skills without overwhelming the context window.

## Key Features

- **Progressive Disclosure**: Load instructions and resources on-demand
- **Framework Agnostic**: Works with any AI framework (LangChain, LlamaIndex, raw API)
- **Type Safe**: Full Pydantic models and type hints
- **Extensible**: Add skills by following a simple directory structure
- **Production Ready**: Tests and examples included

## Quick Start

### 1. Create a Skill Directory

```
skills/
└── my_skill/
    ├── metadata.json   # Level 1
    ├── SKILL.md        # Level 2
    └── resources/      # Level 3 (optional)
        └── example.py
```

### 2. Add `metadata.json`

```json
{
  "name": "My Skill",
  "description": "Brief description for the agent to decide if this skill is relevant.",
  "version": "1.0.0",
  "tags": ["tag1", "tag2"]
}
```

### 3. Add `SKILL.md`

```markdown
# My Skill

## Purpose
When to use this skill.

## Instructions
Step-by-step instructions for the agent.

## Resources
- `resources/example.py` - Reference this when needed.
```

### 4. API Usage

```bash
# Level 1: List metadata (for system prompt)
GET /api/v1/skills

# Level 2: Get full skill when agent selects it
GET /api/v1/skills/my_skill

# Level 3: Get resource when instructions reference it
GET /api/v1/skills/my_skill/resources/example.py
```

### 5. Integration Pattern

1. **System prompt**: Include `GET /api/v1/skills` metadata for each skill
2. **Agent selects skill**: Call `GET /api/v1/skills/{id}` for full instructions
3. **Agent needs resource**: Call `GET /api/v1/skills/{id}/resources/{path}`

Configure `SKILLS_DIR` in `.env` to point to your skills directory (default: `skills`).
