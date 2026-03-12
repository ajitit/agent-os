# LLM Module

## Purpose
Abstracts all LLM provider interactions behind a unified adapter interface. Manages model listings and the model registry.

## Responsibilities
- Provide `LLMBase` abstract interface for all LLM providers
- Implement OpenAI provider (current)
- Expose model listing endpoint
- Manage model registry (CRUD for available models)
- Support Anthropic and other providers (planned)

## Technology Stack
- `langchain-openai` — OpenAI integration
- `langchain` — base LLM abstractions
- Python 3.11+, FastAPI

## Key Directories
```
backend/
├── adapters/llm/
│   ├── base.py         # Abstract LLMBase interface
│   └── openai.py       # OpenAI implementation
├── api/llm.py          # GET /llm/models endpoint
└── api/model_registry.py  # Model registry CRUD
```

## Important Files
| File | Role |
|------|------|
| `adapters/llm/base.py` | Abstract LLMBase — all providers implement this |
| `adapters/llm/openai.py` | OpenAI concrete implementation |
| `api/llm.py` | `GET /api/v1/llm/models` — list available models |
| `api/model_registry.py` | CRUD for model registry entries |

## Data Flow
```
Agent config (model: str) → LLM Adapter factory
  → OpenAIAdapter.complete(prompt, messages)
  → OpenAI API → response tokens
  → streamed to conversation via SSE
```

## External Dependencies
- `OPENAI_API_KEY` — required env var
- `ANTHROPIC_API_KEY` — optional (planned)
- OpenAI API (gpt-4, gpt-4o, etc.)

## Development Rules
- **Never** import OpenAI SDK directly outside `adapters/llm/`
- All new LLM providers implement `LLMBase` from `adapters/llm/base.py`
- Model IDs stored as strings; validated against registry
- API key config via `settings.openai_api_key` (never hardcoded)
