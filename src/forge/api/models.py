from datetime import datetime
from enum import Enum
from typing import Optional, List, Any, Dict

from pydantic import BaseModel


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ERROR = "error"


class TaskBase(BaseModel):
    name: str
    description: Optional[str] = None
    yaml_content: str  # The raw YAML content of the test case


class TaskCreate(TaskBase):
    pass


class Task(TaskBase):
    id: str
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    
    # Execution info could be added here later
    execution_id: Optional[str] = None

    class Config:
        from_attributes = True


class TaskSummary(BaseModel):
    id: str
    name: str
    status: TaskStatus
    created_at: datetime


class ExecutionLog(BaseModel):
    timestamp: datetime
    level: str
    message: str


class CellExecutionState(BaseModel):
    id: str
    status: str  # pending, running, success, error
    code: str
    output: Optional[str] = None


class ExecutionState(BaseModel):
    task_id: str
    status: TaskStatus
    logs: List[ExecutionLog] = []
    cells: List[CellExecutionState] = []
