from typing import Dict, Optional, List, Any
import asyncio
from datetime import datetime

from .models import Task, TaskStatus
from ..runtime.session import JupyterNotebookSession

class TaskStore:
    def __init__(self):
        self._tasks: Dict[str, Task] = {}
        # Stores the runtime session/state associated with a task
        self._executions: Dict[str, dict] = {} 
        self._sessions: Dict[str, JupyterNotebookSession] = {}

    def create_session(self, task_id: str) -> JupyterNotebookSession:
        """Create or retrieve a session for the task."""
        if task_id not in self._sessions:
            session = JupyterNotebookSession(name=f"session_{task_id}")
            session.start()
            self._sessions[task_id] = session
        return self._sessions[task_id]

    def get_session(self, task_id: str) -> Optional[JupyterNotebookSession]:
        return self._sessions.get(task_id)

    def close_session(self, task_id: str):
        if task_id in self._sessions:
            session = self._sessions[task_id]
            try:
                session.stop()
            except Exception as e:
                print(f"Error closing session {task_id}: {e}")
            del self._sessions[task_id]

    def create_task(self, task: Task) -> Task:
        self._tasks[task.id] = task
        self._executions[task.id] = {
            "logs": [],
            "cells": [],
            "status": TaskStatus.PENDING
        }
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)

    def list_tasks(self, skip: int = 0, limit: int = 100) -> List[Task]:
        tasks = list(self._tasks.values())
        # Sort by created_at desc
        tasks.sort(key=lambda x: x.created_at, reverse=True)
        return tasks[skip : skip + limit]

    def delete_task(self, task_id: str) -> bool:
        if task_id in self._tasks:
            del self._tasks[task_id]
            if task_id in self._executions:
                del self._executions[task_id]
            self.close_session(task_id)
            return True
        return False

    def update_status(self, task_id: str, status: TaskStatus):
        if task_id in self._tasks:
            self._tasks[task_id].status = status
            self._tasks[task_id].updated_at = datetime.now()

    def get_execution_state(self, task_id: str) -> Optional[dict]:
        return self._executions.get(task_id)

    def append_log(self, task_id: str, level: str, message: str):
        if task_id in self._executions:
            self._executions[task_id]["logs"].append({
                "timestamp": datetime.now(),
                "level": level,
                "message": message
            })

    def update_cells(self, task_id: str, cells: List[dict]):
        if task_id in self._executions:
            self._executions[task_id]["cells"] = cells

# Global instance
store = TaskStore()
