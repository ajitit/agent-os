# System Design Checklist

## Before Implementing
- [ ] Module boundary defined — which directory/file owns this?
- [ ] Layer respected — UI → API → Core → Adapters (no skipping layers)
- [ ] Registry pattern applied if resource is manageable CRUD entity
- [ ] Adapter pattern applied if external service dependency
- [ ] Backward compatibility considered for existing API consumers
- [ ] In-memory store sufficient, or DB migration needed?

## API Design
- [ ] Route follows `/api/v1/{plural-resource}` convention
- [ ] All handlers are `async def`
- [ ] Response uses `APIResponse[T]`
- [ ] Error uses `AgentOSException`
- [ ] Pydantic model defined for request/response
- [ ] Auth required (unless `/health` or `/auth`)

## Scalability
- [ ] No in-memory state that grows unbounded without eviction
- [ ] External calls go through adapters (mockable for testing)
- [ ] Pipeline stages are stateless (context passed explicitly)
- [ ] LLM calls are async and non-blocking

## Documentation
- [ ] Module doc updated in `docs/modules/`
- [ ] Module map updated in `docs/module-map.md`
- [ ] AI_CONTEXT file updated if key files changed
