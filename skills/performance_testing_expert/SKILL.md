# Performance Testing Expert Skill

## Purpose
Use this skill when benchmarking Vishwakarma endpoints, running load tests, validating scalability, or identifying performance bottlenecks in the API, pipeline, or LLM response flows.

## Context Sources
- `docs/ARCHITECTURE.md` — system layers, external dependencies, deployment model
- `docs/modules/backend.md` — backend structure, async patterns
- `docs/modules/infra.md` — Docker deployment, environment configuration
- `docs/modules/llm.md` — LLM adapter flow and external API calls

## Workflow
1. **Define targets** — Identify endpoints or flows to benchmark
2. **Set baselines** — Document current response times and throughput
3. **Design test plan** — Reference `resources/performance_test_strategy.md`
4. **Identify risks** — Check for blocking I/O, synchronous LLM calls, large payloads
5. **Execute load tests** — Use patterns from `resources/load_testing_patterns.md`
6. **Analyze results** — Identify p50/p95/p99 latencies, error rates, throughput limits
7. **Find bottlenecks** — Profile slow paths (LLM latency, pipeline stages, DB queries)
8. **Report** — Produce findings with optimization recommendations

## Rules
- All API handlers must be `async def` — flag any synchronous blocking code
- LLM calls are the primary latency source — always measure separately
- Pipeline stages must not block the event loop
- Rate limit is 60 req/min — load tests must respect this or test on isolated env
- Target benchmarks: API health < 50ms, CRUD ops < 200ms, LLM chat < 3s (first token)
- Test streaming endpoints separately (SSE / chunk latency)

## Output Expectations
Performance report:
```
## Performance Test Summary
- Endpoints tested: [list]
- Concurrency: X users / Y requests

## Results
| Endpoint | p50 | p95 | p99 | Error Rate |
|----------|-----|-----|-----|------------|

## Bottlenecks Found
- [endpoint/module] — issue — recommendation

## Optimization Recommendations
- [priority] action
```

## Resources
- `resources/performance_test_strategy.md` — benchmarking approach for Vishwakarma
- `resources/load_testing_patterns.md` — load test scenarios and tools
