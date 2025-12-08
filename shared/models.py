from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class AgentRequest(BaseModel):
    user_id: str
    prompt: str
    context: Optional[Dict[str, Any]] = {}
    tools: Optional[List[str]] = []

class AgentResponse(BaseModel):
    task_id: str
    status: TaskStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    timestamp: datetime

class ToolCall(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]
    caller_agent: str

class ToolResult(BaseModel):
    tool_name: str
    result: Any
    success: bool
    error: Optional[str] = None

class DataQuery(BaseModel):
    query_type: str
    query: str
    user_id: Optional[str] = None

class DataResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None

class AgentTask(BaseModel):
    task_id: str
    agent_type: str
    payload: Dict[str, Any]
    priority: int = 1
    created_at: datetime

