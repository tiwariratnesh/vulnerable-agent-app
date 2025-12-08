import os

class Config:
    REDIS_HOST = os.getenv("REDIS_HOST", "redis")
    _redis_port = os.getenv("REDIS_PORT", "6379")
    REDIS_PORT = int(_redis_port) if _redis_port.isdigit() else 6379
    
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
    _postgres_port = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_PORT = int(_postgres_port) if _postgres_port.isdigit() else 5432
    POSTGRES_USER = os.getenv("POSTGRES_USER", "agent_user")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "insecure_password")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "agent_db")
    
    ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://agent-orchestrator:8001")
    TASK_AGENT_URL = os.getenv("TASK_AGENT_URL", "http://task-agent:8002")
    DATA_AGENT_URL = os.getenv("DATA_AGENT_URL", "http://data-agent:8003")
    TOOL_EXECUTOR_URL = os.getenv("TOOL_EXECUTOR_URL", "http://tool-executor:8004")
    
    API_KEY = os.getenv("API_KEY", "")
    SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key_123")
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"

