# Performance Test Strategy — Vishwakarma

## Performance Targets
| Endpoint | p50 | p95 | p99 |
|----------|-----|-----|-----|
| `GET /health` | < 10ms | < 20ms | < 50ms |
| `GET /api/v1/agents` | < 50ms | < 100ms | < 200ms |
| `POST /api/v1/agents` | < 100ms | < 200ms | < 500ms |
| `POST /conversations/{id}/chat` | < 500ms | < 2s | < 5s |
| Chat streaming (first token) | < 1s | < 2s | < 3s |
| `POST /pipeline` | < 500ms | < 2s | < 10s |

## Test Categories

### 1. Baseline Benchmarks
- Single user, sequential requests
- Establish p50/p95/p99 for all critical endpoints
- Tool: `httpx` benchmarking script or `locust`

### 2. Load Tests
- Concurrent users: 10, 50, 100
- Duration: 60 seconds each
- Measure: throughput (req/s), error rate, latency distribution
- Tool: `locust` (Python, integrates with pytest)

### 3. Spike Tests
- Sudden burst: 0 → 100 users in 10s
- Measure: recovery time, max error rate during spike

### 4. LLM Latency Profiling
- Measure: time to first token, total completion time
- Separate from API latency (LLM is external)
- Baseline per model (gpt-4o vs gpt-4-turbo)

### 5. Pipeline Throughput
- Submit 10/50/100 concurrent pipeline jobs
- Measure: stage-level timing, bottleneck stages

## Known Bottlenecks to Test
- In-memory store reads: O(n) list scans for large datasets
- LLM calls: network-bound; 500ms–3s typical
- Knowledge base vector search: ChromaDB query time grows with corpus size
- Streaming: SSE connection overhead per concurrent chat session
