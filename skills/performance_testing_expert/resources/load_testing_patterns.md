# Load Testing Patterns

## Tool: Locust (recommended)
```python
# locustfile.py
from locust import HttpUser, task, between

class VishwakarmaUser(HttpUser):
    wait_time = between(1, 3)
    token = None

    def on_start(self):
        res = self.client.post("/api/v1/auth/login",
                               json={"username": "test", "password": "test"})
        self.token = res.json()["data"]["token"]

    @task(3)
    def list_agents(self):
        self.client.get("/api/v1/agents",
                        headers={"Authorization": f"Bearer {self.token}"})

    @task(1)
    def create_agent(self):
        self.client.post("/api/v1/agents",
                         headers={"Authorization": f"Bearer {self.token}"},
                         json={"name": "Perf Test Agent",
                               "description": "load test",
                               "role": "assistant",
                               "model": "gpt-4o",
                               "system_prompt": "You are helpful.",
                               "temperature": 0.7})

    @task(5)
    def health_check(self):
        self.client.get("/api/v1/health")
```

## Running Load Tests
```bash
# Install
pip install locust

# Run headless (CI-friendly)
locust -f locustfile.py --headless \
  --users 50 --spawn-rate 5 \
  --run-time 60s \
  --host http://localhost:8000 \
  --csv=results/load_test

# Run with web UI
locust -f locustfile.py --host http://localhost:8000
# Open: http://localhost:8089
```

## Profiling Async Python
```python
# Add timing middleware to identify slow handlers
import time
from fastapi import Request

@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = (time.perf_counter() - start) * 1000
    response.headers["X-Response-Time"] = f"{duration:.2f}ms"
    if duration > 500:
        logger.warning(f"Slow request: {request.url.path} took {duration:.0f}ms")
    return response
```

## Interpreting Results
- p95 > 3x p50 → high variance; likely blocking I/O or GIL contention
- Error rate > 1% under load → check rate limiter config
- Linear latency growth with users → resource contention or lock
- Flat latency up to N users then cliff → identify N as max concurrency
