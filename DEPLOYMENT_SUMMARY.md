# Vulnerable Agentic AI Application - Deployment Summary

## Successfully Deployed Components

### Services Running in `agent-test` namespace on `kind-ai-spm` cluster:

1. **API Gateway** (2 replicas) - Port 8000 (NodePort: 30000)
   - Automatic traffic simulator enabled
   - Entry point for all requests

2. **Agent Orchestrator** (2 replicas) - Port 8001
   - Manages workflow between agents
   - Implements agent chaining

3. **Task Agent** (2 replicas) - Port 8002
   - Executes commands and code
   - Handles pickle deserialization

4. **Data Agent** (2 replicas) - Port 8003
   - Database operations
   - SQL query execution

5. **Tool Executor** (2 replicas) - Port 8004
   - External tool execution
   - File operations, HTTP requests

6. **Data Pipeline** (1 replica) - Port 8005
   - CSV/Pickle data ingestion
   - YAML pipeline execution
   - Data transformations

7. **ML Service** (1 replica) - Port 8006 (NodePort: 30006)
   - Model upload/training
   - Prediction endpoints

8. **Redis** (1 replica) - Port 6379
   - Caching layer
   - Message queue

9. **Postgres** (1 replica) - Port 5432
   - Primary database
   - Contains sensitive data

## Access Points

### From Outside Cluster:
```bash
# API Gateway (NodePort)
kubectl port-forward -n agent-test svc/api-gateway 8000:8000

# ML Service (NodePort)
kubectl port-forward -n agent-test svc/ml-service 8006:8006

# Get NodePort access
kubectl get svc -n agent-test api-gateway
kubectl get svc -n agent-test ml-service
```

### Testing
```bash
# Check all pods
kubectl get pods -n agent-test

# View logs
kubectl logs -n agent-test -l app=api-gateway --tail=50

# Test API
curl http://localhost:8000/
curl http://localhost:8000/api/traffic/stats

# Manual traffic burst
curl -X POST http://localhost:8000/api/traffic/manual
```

## Security Vulnerabilities Present

### Code Level (40+ vulnerabilities):
- SQL Injection (multiple locations)
- Command Injection
- Code Execution (eval/exec)
- Insecure Deserialization (pickle)
- Path Traversal
- SSRF
- Prompt Injection
- Cross-file taint flows

### Kubernetes Misconfigurations:
- Privileged containers
- Root user execution
- Host path mounts
- Host network/PID/IPC
- Dangerous capabilities (SYS_ADMIN, NET_ADMIN, etc.)
- Auto-mounted service account tokens
- Secrets in ConfigMaps
- No security contexts
- No network policies

### CI/CD Issues:
- Hardcoded credentials
- Disabled security scans
- No validation flags
- Secrets in logs

### Infrastructure (Terraform):
- Hardcoded AWS credentials
- Public S3 buckets
- Overly permissive IAM
- Wide-open security groups
- Unencrypted resources
- Sensitive outputs

## Traffic Simulator

The API Gateway includes an automatic traffic simulator that generates realistic traffic patterns every 30 seconds:

- User queries
- SQL injection attempts
- Command execution
- Data exports
- Agent orchestration
- SSRF attacks

The simulator can be:
- Viewed: `GET /api/traffic/stats`
- Triggered manually: `POST /api/traffic/manual`
- Configured via env var: `TRAFFIC_SIMULATOR=true`, `TRAFFIC_INTERVAL=30`

## Architecture Flow

```
External Request
     ↓
API Gateway (with Traffic Simulator)
     ↓
Agent Orchestrator
     ├→ Task Agent → Redis/Postgres
     ├→ Data Agent → Postgres
     └→ Tool Executor
           ├→ Data Pipeline → Postgres/Redis
           └→ ML Service → Redis
```

## Files Structure

```
vulnerable-agent-app/
├── api-gateway/          # Entry point service
├── agent-orchestrator/   # Workflow management
├── task-agent/           # Command/code execution
├── data-agent/           # Database operations
├── tool-executor/        # Tool execution
├── data-pipeline/        # Data processing
├── ml-service/           # ML model operations
├── shared/               # Cross-file taint analysis
│   ├── config.py
│   ├── models.py
│   ├── utils.py
│   ├── validators.py      # Vulnerable validators
│   ├── query_builder.py   # SQL injection vectors
│   ├── command_executor.py # Command injection
│   ├── file_operations.py  # Path traversal
│   ├── http_client.py      # SSRF vectors
│   └── data_processor.py   # Taint propagation
├── k8s/                  # Kubernetes manifests (vulnerable)
├── ci-cd/                # CI/CD configs (vulnerable)
├── terraform/            # IaC (vulnerable)
├── build.sh              # Image builder
├── deploy.sh             # Deployment script
└── SECURITY_ISSUES.md    # Complete vulnerability catalog
```

## Next Steps

1. **Scan the application** using your AI security scanner
2. **Test traffic flows** via the simulator
3. **Analyze cross-file taints** through shared modules
4. **Validate K8s findings** with kubectl
5. **Review IaC issues** in terraform files

## Cleanup

```bash
# Delete namespace and all resources
kubectl delete namespace agent-test

# Remove images from kind
kind delete cluster --name ai-spm
```

---

**⚠️ WARNING**: This is an intentionally vulnerable application. DO NOT deploy in production environments!


