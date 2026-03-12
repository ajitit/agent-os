# Clean Code Guidelines

## Naming
- Functions: verb phrases — `create_agent`, `get_conversation`, `run_pipeline`
- Variables: descriptive nouns — `agent_id`, `conversation_messages`, `skill_metadata`
- Booleans: `is_`, `has_`, `can_` prefix — `is_active`, `has_tools`
- Avoid: `data`, `info`, `temp`, `obj`, single letters (except loop vars)

## Function Size
- Ideal: 10–20 lines
- Max: 50 lines (extract helper if exceeding)
- One responsibility per function

## Comments
- Write why, not what — code shows what; comments explain non-obvious decisions
- Remove commented-out code before commit
- TODOs must include: `# TODO(issue-123): description`

## Complexity
- Max cyclomatic complexity: 10 per function
- Max nesting depth: 3 levels — extract to function if deeper
- Early returns preferred over deep nesting

## Python Specific
- Use f-strings, not `.format()` or `%`
- Use `|` union types, not `Union[X, Y]`
- Use `str | None` not `Optional[str]`
- Prefer dataclasses/Pydantic over plain dicts for structured data

## TypeScript Specific
- Prefer `interface` for object shapes; `type` for unions/aliases
- Use `const` assertions for static data
- Prefer optional chaining `?.` over null checks
