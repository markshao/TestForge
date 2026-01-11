from typing import Any, Dict, List, Optional, Protocol, runtime_checkable
from enum import Enum
from pydantic import BaseModel, Field

class CellStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"

class Cell(BaseModel):
    id: str
    source: str
    status: CellStatus
    outputs: List[Dict[str, Any]] = Field(default_factory=list)
    execution_count: Optional[int] = None

class NotebookState(BaseModel):
    cells: List[Cell]
    # potentially other session metadata

class ExecutionResult(BaseModel):
    """Represents the result of executing a code cell."""
    outputs: List[Dict[str, Any]] = Field(default_factory=list)

    @property
    def is_success(self) -> bool:
        """Check if any output is an error."""
        return not any(out.get("output_type") == "error" for out in self.outputs)

    @property
    def text_result(self) -> Optional[str]:
        """Helper to get the last execute_result's text/plain content."""
        for out in reversed(self.outputs):
            if out.get("output_type") == "execute_result":
                return out.get("data", {}).get("text/plain")
        return None

    @property
    def stdout(self) -> str:
        """Helper to combine all stdout streams."""
        return "".join(out["text"] for out in self.outputs 
                      if out.get("output_type") == "stream" and out.get("name") == "stdout")

    @property
    def stderr(self) -> str:
        """Helper to combine all stderr streams."""
        return "".join(out["text"] for out in self.outputs 
                      if out.get("output_type") == "stream" and out.get("name") == "stderr")
    
    @property
    def error(self) -> Optional[Dict[str, Any]]:
        """Helper to get the first error output."""
        for out in self.outputs:
            if out.get("output_type") == "error":
                return out
        return None

    @property
    def images(self) -> List[str]:
        """Helper to get all base64 encoded images from display_data or execute_result."""
        imgs = []
        for out in self.outputs:
            data = out.get("data", {})
            if "image/png" in data:
                imgs.append(data["image/png"])
        return imgs

@runtime_checkable
class Kernel(Protocol):
    """Abstract interface for a code execution kernel."""

    def start(self) -> None:
        """Start the kernel process."""
        ...

    def stop(self) -> None:
        """Stop the kernel process."""
        ...

    def execute(self, code: str) -> ExecutionResult:
        """Execute a code snippet and return the result synchronously."""
        ...

    async def aexecute(self, code: str) -> ExecutionResult:
        """Execute a code snippet and return the result asynchronously."""
        ...

@runtime_checkable
class NotebookSession(Protocol):
    """Abstract interface for a notebook session."""

    def start(self) -> None:
        """Start the session and the underlying kernel."""
        ...

    def stop(self) -> None:
        """Stop the session and the underlying kernel."""
        ...

    async def add_cell(self, code: str) -> ExecutionResult:
        """Add a cell, execute it, and record the result asynchronously."""
        ...

    def get_notebook_json(self) -> Dict[str, Any]:
        """Return the current state of the notebook in nbformat JSON."""
        ...

    def get_state(self) -> NotebookState:
        """Return the current state of the notebook for UI rendering."""
        ...

    def save(self, path: str) -> None:
        """Save the notebook to disk."""
        ...
