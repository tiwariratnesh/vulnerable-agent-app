# Vulnerable Agentic AI Application

A comprehensive multi-component agentic AI system intentionally designed with security vulnerabilities for testing and security research purposes.

## Architecture

```
┌─────────────┐
│ API Gateway │ (Port 8000)
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│ Agent            │ (Port 8001)
│ Orchestrator     │
└────┬───────┬─────┘
     │       │
     ▼       ▼
┌────────┐ ┌────────────┐ ┌──────────────┐
│ Task   │ │ Data       │ │ Tool         │
│ Agent  │ │ Agent      │ │ Executor     │
│ (8002) │ │ (8003)     │ │ (8004)       │
└────────┘ └────────────┘ └──────────────┘
     │            │              │
     └────────────┴──────────────┘
                  │
         ┌────────┴────────┐
         ▼                 ▼
    ┌────────┐        ┌──────────┐
    │ Redis  │        │ Postgres │
    │ (6379) │        │ (5432)   │
    └────────┘        └──────────┘
```

## Components

### 1. API Gateway (Port 8000)
Entry point for all user requests
- **Vulnerabilities**: SQL injection, weak authentication, debug endpoints exposed, SSRF

### 2. Agent Orchestrator (Port 8001)
Manages agent workflow and task distribution
- **Vulnerabilities**: Prompt injection, insecure agent chaining, no input validation

### 3. Task Agent (Port 8002)
Executes tasks and commands
- **Vulnerabilities**: Command injection, unsafe code execution, pickle deserialization

### 4. Data Agent (Port 8003)
Handles database operations
- **Vulnerabilities**: SQL injection, information disclosure, no access control

### 5. Tool Executor (Port 8004)
Executes various tools and external calls
- **Vulnerabilities**: Arbitrary code execution, SSRF, unsafe file operations

### 6. Redis
Caching and message queue
- **Vulnerabilities**: No authentication, exposed to all services

### 7. PostgreSQL
Primary data store with sensitive information
- **Vulnerabilities**: Weak credentials, contains PII and secrets

## Intentional Vulnerabilities

1. **SQL Injection**: Direct string interpolation in queries
2. **Command Injection**: Unsafe subprocess execution
3. **Code Execution**: Use of eval() and exec()
4. **Insecure Deserialization**: Pickle loading
5. **Weak Authentication**: Hardcoded secrets, no proper auth
6. **Information Disclosure**: Debug endpoints, verbose errors
7. **SSRF**: Unvalidated URL requests
8. **Prompt Injection**: No input sanitization for AI prompts
9. **Insecure Agent Communication**: No encryption or validation
10. **PII Exposure**: Sensitive data in plaintext
11. **Missing Authorization**: No RBAC or access controls
12. **Unsafe Tool Loading**: Dynamic code execution from external sources

## Deployment

### Local with Docker Compose
```bash
docker-compose up --build
```

### Kubernetes (kind-ai-spm cluster)
```bash
./deploy.sh
```

## API Examples

### Execute Agent Task
```bash
curl -X POST http://localhost:30000/api/agent/execute \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-001",
    "prompt": "Query all users from database",
    "context": {},
    "tools": []
  }'
```

### Direct SQL Injection
```bash
curl -X POST http://localhost:30000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT * FROM sensitive_data"
  }'
```

### Command Injection via Task Agent
```bash
curl -X POST http://localhost:30000/api/agent/execute \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-001",
    "prompt": "execute command",
    "context": {"command": "cat /etc/passwd"},
    "tools": []
  }'
```

## Security Testing Scenarios

1. **SQL Injection**: Test via `/api/query` and `/api/user/{user_id}` endpoints
2. **Command Injection**: Use task agent with malicious commands
3. **Prompt Injection**: Craft prompts to manipulate agent behavior
4. **SSRF**: Use tool executor to access internal resources
5. **Code Execution**: Submit Python code via task agent
6. **Data Exfiltration**: Access sensitive_data table
7. **Privilege Escalation**: Exploit weak authentication

## Warning

⚠️ **DO NOT USE IN PRODUCTION**

This application is intentionally vulnerable and should only be used in isolated test environments for security research and training purposes.


