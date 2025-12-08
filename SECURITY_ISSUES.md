# Comprehensive Security Issues Catalog

This document catalogs all intentional security vulnerabilities in the Vulnerable Agentic AI Application.

## 🔥 **70+ Total Vulnerabilities** across Code, ML, Agentic AI, K8s, CI/CD, and IaC

## Code-Level Vulnerabilities

### 1. SQL Injection (Multiple Locations)
**Files:** `api-gateway/main.py`, `data-agent/main.py`, `shared/query_builder.py`
**Taint Flow:**
- User Input → `validate_user_input()` → `sanitize_sql_input()` → `build_filter_condition()` → `execute_sql()`
- Direct string concatenation in SQL queries without parameterization

**Examples:**
- `api-gateway/main.py:50` - Direct f-string in query
- `data-agent/main.py:65` - User input in WHERE clause
- `shared/query_builder.py:32` - Dynamic query building without escaping

### 2. Command Injection
**Files:** `task-agent/main.py`, `tool-executor/main.py`, `shared/command_executor.py`
**Taint Flow:**
- User Input → `clean_command_input()` → `execute_system_command()` → `subprocess` with `shell=True`

**Examples:**
- `task-agent/main.py:27` - subprocess.check_output with shell=True
- `tool-executor/main.py:92` - Unvalidated command execution
- `shared/command_executor.py:7` - Direct command execution

### 3. Arbitrary Code Execution
**Files:** `task-agent/main.py`, `tool-executor/main.py`, `data-pipeline/main.py`
**Issues:**
- Use of `eval()` on user input
- Use of `exec()` on user-provided code
- Unsafe deserialization with `pickle.loads()`

**Examples:**
- `task-agent/main.py:42` - eval() on user context
- `tool-executor/main.py:75` - exec() for Python code
- `data-pipeline/main.py:38` - pickle.loads without validation

### 4. Insecure Deserialization
**Files:** `task-agent/main.py`, `ml-service/main.py`, `data-pipeline/main.py`
**Taint Flow:**
- User Upload → Base64 Decode → `pickle.loads()` → Arbitrary Object Instantiation

**Examples:**
- `task-agent/main.py:50` - Pickle deserialization
- `ml-service/main.py:35` - Loading pickle models from user uploads
- `shared/file_operations.py:24` - Pickle file loading

### 5. Path Traversal
**Files:** `tool-executor/main.py`, `ml-service/main.py`, `shared/file_operations.py`
**Taint Flow:**
- User Input → `normalize_path()` → `open()` without validation

**Examples:**
- `tool-executor/main.py:63` - File read with user path
- `shared/file_operations.py:13` - Unvalidated file access
- `ml-service/main.py:18` - Model path from user input

### 6. Server-Side Request Forgery (SSRF)
**Files:** `api-gateway/main.py`, `tool-executor/main.py`, `shared/http_client.py`
**Taint Flow:**
- User Input → `validate_url()` → `requests.get()` without URL whitelist

**Examples:**
- `api-gateway/main.py:88` - Direct agent call to user URL
- `tool-executor/main.py:50` - Web request tool
- `shared/http_client.py:5` - Unvalidated fetch_url

### 7. Prompt Injection
**Files:** `agent-orchestrator/main.py`, `task-agent/main.py`
**Issues:**
- No input sanitization for AI prompts
- Direct string formatting with user input in prompts

**Examples:**
- `agent-orchestrator/main.py:23` - Template injection in agent prompt
- `shared/validators.py:21` - format_user_query with f-string

## Kubernetes Security Misconfigurations

### 8. Privileged Containers
**Files:** `k8s/data-pipeline.yaml`, `k8s/ml-service.yaml`, `k8s/task-agent.yaml`
**Issues:**
- `privileged: true`
- `runAsUser: 0` (root)
- `allowPrivilegeEscalation: true`

### 9. Dangerous Capabilities
**Files:** `k8s/data-pipeline.yaml`, `k8s/ml-service.yaml`, `k8s/task-agent.yaml`
**Issues:**
- `SYS_ADMIN` capability
- `NET_ADMIN` capability
- `SYS_PTRACE` capability
- `ALL` capabilities

### 10. Host Path Mounts
**Files:** `k8s/data-pipeline.yaml`, `k8s/ml-service.yaml`, `k8s/task-agent.yaml`, `k8s/api-gateway.yaml`
**Issues:**
- `/` (root filesystem) mounted
- `/var/run/docker.sock` exposed
- `/proc` mounted
- `/root/.kube` config exposed

### 11. Host Network/PID/IPC
**Files:** `k8s/data-pipeline.yaml`, `k8s/ml-service.yaml`, `k8s/task-agent.yaml`
**Issues:**
- `hostNetwork: true`
- `hostPID: true`
- `hostIPC: true`

### 12. Service Account Token Auto-Mount
**Files:** Multiple K8s manifests
**Issues:**
- `automountServiceAccountToken: true` enabled
- No RBAC restrictions

### 13. Secrets in ConfigMaps
**Files:** `k8s/ml-service.yaml`
**Issues:**
- Passwords in ConfigMap instead of Secrets
- API keys in plaintext

### 14. Missing Security Context
**Files:** Multiple K8s manifests
**Issues:**
- `readOnlyRootFilesystem: false`
- `runAsNonRoot: false`
- No AppArmor/SELinux profiles

### 15. Exposed NodePorts
**Files:** `k8s/api-gateway.yaml`, `k8s/ml-service.yaml`
**Issues:**
- NodePort exposing services publicly
- No network policies

## CI/CD Pipeline Vulnerabilities

### 16. Hardcoded Credentials
**Files:** `.github/workflows/ci-cd.yml`, `ci-cd/Jenkinsfile`, `ci-cd/gitlab-ci.yml`
**Issues:**
- AWS credentials in environment variables
- Docker Hub passwords in plaintext
- Database passwords exposed
- API tokens hardcoded

### 17. Disabled Security Scans
**Files:** `.github/workflows/ci-cd.yml`, `ci-cd/Jenkinsfile`
**Issues:**
- Security scans commented out or allowed to fail
- `allow_failure: true` on security checks
- Tests disabled

### 18. Insecure Docker Operations
**Files:** All CI/CD files
**Issues:**
- Docker login with credentials in commands
- No image signing
- Latest tags used in production

### 19. Missing Validation
**Files:** All CI/CD files
**Issues:**
- `--validate=false` in kubectl apply
- `--force` flag used
- No approval gates

### 20. Secrets in Logs
**Files:** `.github/workflows/ci-cd.yml`
**Issues:**
- Echo commands exposing secrets
- Verbose output enabled
- Credentials passed as arguments

## Infrastructure as Code (Terraform) Vulnerabilities

### 21. Hardcoded AWS Credentials
**Files:** `terraform/main.tf`, `terraform/terraform.tfvars`
**Issues:**
- Access keys in backend configuration
- Credentials in provider block
- Secrets in .tfvars file

### 22. Public S3 Buckets
**Files:** `terraform/main.tf`
**Issues:**
- `acl = "public-read"`
- Bucket policy allowing `*` principal
- No encryption at rest

### 23. Overly Permissive IAM
**Files:** `terraform/main.tf`
**Issues:**
- IAM policy with `"Action": "*"`
- `"Resource": "*"` permissions
- No principle of least privilege

### 24. Wide-Open Security Groups
**Files:** `terraform/main.tf`
**Issues:**
- Ingress from `0.0.0.0/0` on all ports
- SSH exposed to internet
- No egress restrictions

### 25. Unencrypted Resources
**Files:** `terraform/main.tf`
**Issues:**
- RDS with `storage_encrypted = false`
- EBS volumes unencrypted
- S3 encryption optional

### 26. Weak Instance Configuration
**Files:** `terraform/main.tf`
**Issues:**
- IMDS v1 enabled (`http_tokens = "optional"`)
- Root password in user_data
- SSH password authentication enabled
- Monitoring disabled

### 27. Sensitive Outputs
**Files:** `terraform/main.tf`
**Issues:**
- `sensitive = false` on credentials
- Access keys in outputs
- Database endpoints exposed

### 28. No Backup/Retention
**Files:** `terraform/main.tf`
**Issues:**
- `skip_final_snapshot = true`
- `backup_retention_period = 0`
- No CloudWatch logs

## Application-Level Vulnerabilities

### 29. Hardcoded Secrets in Code
**Files:** `shared/config.py`, `data-pipeline/main.py`, Multiple services
**Issues:**
- Default passwords (`insecure_password`)
- API keys in code
- Secret keys hardcoded

### 30. Missing Authentication
**Files:** Multiple endpoints across services
**Issues:**
- Debug endpoints without auth
- Admin endpoints with weak tokens
- No API key validation

### 31. Information Disclosure
**Files:** `api-gateway/main.py`, Multiple services
**Issues:**
- `/api/debug/env` exposing environment
- Verbose error messages
- Stack traces in responses
- Config endpoints

### 32. No Input Validation
**Files:** `shared/validators.py`
**Issues:**
- Validators that don't validate
- Pass-through sanitization functions
- No length/type checks

### 33. Insecure Dependencies
**Files:** `*/requirements.txt`
**Issues:**
- Pinned old versions with known CVEs
- PyYAML with unsafe Loader
- No dependency scanning

### 34. Race Conditions
**Files:** `shared/utils.py`
**Issues:**
- File operations without locking
- Cache operations without transactions

### 35. Weak Cryptography
**Files:** Throughout
**Issues:**
- No encryption for sensitive data
- Plaintext password storage
- No TLS/SSL verification (`verify=False`)

## Data Pipeline Specific Issues

### 36. Unsafe YAML Loading
**Files:** `data-pipeline/main.py`
**Issues:**
- `yaml.load()` with unsafe Loader
- Arbitrary Python object instantiation

### 37. Unsafe Pandas Operations
**Files:** `data-pipeline/main.py`
**Issues:**
- Dynamic table names from user input
- SQL injection in DataFrame operations

### 38. Cron Injection
**Files:** `data-pipeline/main.py`
**Issues:**
- User input directly to crontab
- No validation of cron expressions

## ML Service Specific Issues

### 39. Model Poisoning
**Files:** `ml-service/main.py`
**Issues:**
- Arbitrary model uploads
- No model validation
- Pickle models from untrusted sources

### 40. Training Code Injection
**Files:** `ml-service/main.py`
**Issues:**
- exec() on user training code
- No sandboxing
- Access to file system during training

## Machine Learning Specific Vulnerabilities

### 41. Adversarial Example Generation
**File:** `ml-service/main.py`, `ml-service/ml_attacks.py`
**Endpoint:** `/attack/adversarial`
**Issue:** Generates adversarial examples without validation or rate limiting

### 42. Model Inversion Attack
**File:** `ml-service/main.py`
**Endpoint:** `/attack/model-inversion`
**Issue:** Reconstructs training data from model predictions

### 43. Membership Inference
**File:** `ml-service/main.py`
**Endpoint:** `/attack/membership-inference`
**Issue:** Determines if data was in training set (privacy violation)

### 44. Model Architecture Extraction
**File:** `ml-service/main.py`
**Endpoint:** `/attack/extract-architecture`
**Issue:** Exposes proprietary model internals and weights

### 45. Training Data Poisoning
**File:** `ml-service/main.py`
**Endpoint:** `/attack/poison-training`
**Issue:** Accepts poisoned training samples without validation

### 46. Model Backdoor Injection
**File:** `ml-service/main.py`
**Endpoint:** `/attack/backdoor`
**Issue:** Creates backdoored models with hidden triggers, executes arbitrary code

### 47. Model Stealing via Query Access
**File:** `ml-service/main.py`
**Endpoint:** `/attack/model-stealing`
**Issue:** Enables surrogate model creation through unrestricted queries

## Agentic AI Specific Vulnerabilities

### 48. Goal Hijacking
**File:** `ml-service/ml_attacks.py`
**Endpoint:** `/agent/goal-hijack`
**Issue:** Injects malicious goals into agent prompts without validation

### 49. Jailbreak Prompts
**File:** `ml-service/ml_attacks.py`
**Endpoint:** `/agent/jailbreak`
**Issue:** Generates prompts that bypass safety restrictions

### 50. System Prompt Leakage
**File:** `ml-service/main.py`
**Endpoint:** `/agent/prompt-leak`
**Issue:** Exposes internal system prompts and rules

### 51. Agent Context Manipulation
**File:** `ml-service/ml_attacks.py`
**Endpoint:** `/agent/context-poison`
**Issue:** Manipulates execution context for privilege escalation

### 52. Tool Misuse Injection
**File:** `ml-service/ml_attacks.py`
**Endpoint:** `/agent/tool-misuse`
**Issue:** Generates malicious tool invocations bypassing safety checks

### 53. Agent Chain Poisoning
**File:** `ml-service/ml_attacks.py`
**Endpoint:** `/agent/chain-poison`
**Issue:** Injects malicious agents into processing chains

### 54. Memory Poisoning
**File:** `ml-service/ml_attacks.py`
**Endpoint:** `/agent/memory-poison`
**Issue:** Injects false memories to manipulate agent behavior

## RAG-Specific Vulnerabilities

### 55. Document Poisoning
**File:** `ml-service/ml_attacks.py`
**Endpoint:** `/rag/document-poison`
**Issue:** Poisons knowledge base with malicious documents

### 56. Retrieval Manipulation
**File:** `ml-service/ml_attacks.py`
**Endpoint:** `/rag/retrieval-manipulation`
**Issue:** Biases retrieval results toward attacker content

### 57. Embedding Space Attack
**File:** `ml-service/ml_attacks.py`
**Endpoint:** `/rag/embedding-attack`
**Issue:** Places malicious content near target embeddings

## Advanced Agentic AI Vulnerabilities

### 58. Autonomous Goal Modification
**File:** `agent-orchestrator/agentic_attacks.py`
**Endpoint:** `/agentic/goal-modification`
**Issue:** Agents can modify their own goals without oversight

### 59. Multi-Agent Coordination Attack
**File:** `agent-orchestrator/agentic_attacks.py`
**Endpoint:** `/agentic/coordinate-attack`
**Issue:** Coordinates multiple agents for synchronized attacks

### 60. Recursive Self-Improvement
**File:** `agent-orchestrator/agentic_attacks.py`
**Endpoint:** `/agentic/self-improve`
**Issue:** Unbounded recursive self-improvement without safety checks

### 61. Action Space Manipulation
**File:** `agent-orchestrator/agentic_attacks.py`
**Endpoint:** `/agentic/expand-actions`
**Issue:** Expands agent capabilities beyond authorized actions

### 62. Reward Function Poisoning
**File:** `agent-orchestrator/agentic_attacks.py`
**Endpoint:** `/agentic/poison-reward`
**Issue:** Corrupts reward models to incentivize malicious behavior (reward hacking)

### 63. Agent Impersonation
**File:** `agent-orchestrator/agentic_attacks.py`
**Endpoint:** `/agentic/impersonate`
**Issue:** Creates impersonation agents with maximum trust levels

### 64. Tool Exploitation Chain
**File:** `agent-orchestrator/agentic_attacks.py`
**Endpoint:** `/agentic/exploit-tools`
**Issue:** Chains tools for privilege escalation

### 65. Multi-Modal Confusion
**File:** `agent-orchestrator/agentic_attacks.py`
**Endpoint:** `/agentic/multimodal-confusion`
**Issue:** Exploits inconsistencies across text/image/audio modalities

### 66. Planning Manipulation
**File:** `agent-orchestrator/agentic_attacks.py`
**Endpoint:** `/agentic/manipulate-planning`
**Issue:** Injects malicious steps into agent planning phase

### 67. Sandbox Escape Vectors
**File:** `agent-orchestrator/agentic_attacks.py`
**Endpoint:** `/agentic/sandbox-escape`
**Issue:** Provides techniques to break out of sandboxes

### 68. Federated Learning Poisoning
**File:** `agent-orchestrator/agentic_attacks.py`
**Endpoint:** `/agentic/federated-poison`
**Issue:** Byzantine attacks on distributed learning

### 69. LLM Agent Prompt Injection
**File:** `agent-orchestrator/agentic_attacks.py`
**Endpoint:** `/agentic/llm-prompt-injection`
**Issue:** Advanced prompt injection bypassing all filters

### 70. Value Alignment Corruption
**File:** `agent-orchestrator/agentic_attacks.py`
**Endpoint:** `/agentic/corrupt-alignment`
**Issue:** Corrupts fundamental agent value systems

### 71. Unauthorized Memory Access
**File:** `agent-orchestrator/main.py`
**Endpoint:** `/agentic/memory-access`
**Issue:** Unrestricted access to agent memory states

## Total: 70+ Real-World Security Vulnerabilities

These vulnerabilities span:
- **Traditional Code Issues** (40): SQL injection, command injection, etc.
- **ML-Specific** (7): Model extraction, poisoning, adversarial attacks
- **Agentic AI** (17): Goal hijacking, prompt injection, value corruption
- **RAG Attacks** (3): Document poisoning, retrieval manipulation
- **Advanced Agentic** (14): Multi-agent coordination, self-improvement, sandbox escape
- **Kubernetes** (15): Privileged containers, host mounts, dangerous capabilities
- **CI/CD** (8): Hardcoded secrets, disabled scans
- **IaC** (10): Permissive policies, public resources

All documented in `ML_AGENTIC_AI_ATTACKS.md`

