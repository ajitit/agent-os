# Security Testing Methods for Vishwakarma

## Authentication Tests
```bash
# 1. No token
curl -X GET http://localhost:8000/api/v1/agents
# Expected: 401 Unauthorized

# 2. Expired token (generate and wait, or manually craft)
curl -H "Authorization: Bearer expired.token.here" \
     http://localhost:8000/api/v1/agents
# Expected: 401

# 3. Wrong secret
curl -H "Authorization: Bearer wrongsecret.payload.sig" \
     http://localhost:8000/api/v1/agents
# Expected: 401

# 4. Valid token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
        -d '{"username":"user","password":"pass"}' | jq -r '.data.token')
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/v1/agents
# Expected: 200
```

## Input Validation Tests
```bash
# Missing required field
curl -X POST http://localhost:8000/api/v1/agents \
     -H "Content-Type: application/json" \
     -d '{"description":"no name"}'
# Expected: 422 Validation Error

# Oversized payload
python3 -c "print('A'*100000)" | \
curl -X POST http://localhost:8000/api/v1/agents \
     -H "Content-Type: application/json" -d @-
# Expected: 422 or 413
```

## Rate Limit Test
```bash
for i in $(seq 1 70); do
  curl -s -o /dev/null -w "%{http_code}\n" \
       http://localhost:8000/api/v1/health
done
# Expected: first 60 return 200; after that → 429
```

## CORS Test
```bash
curl -H "Origin: http://evil.com" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS http://localhost:8000/api/v1/agents
# Expected: no Access-Control-Allow-Origin: http://evil.com in response
```

## Secrets Audit
```bash
# Check for secrets in git history
git log --all -p | grep -i "api_key\|secret\|password\|token" | grep "^+" | grep -v ".example"

# Check Docker image layers
docker history --no-trunc vishwakarma-backend | grep -i "secret\|key\|password"
```
