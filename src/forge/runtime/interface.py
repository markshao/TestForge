from typing import Any, Dict, List, Optional, Protocol, runtime_checkable
from pydantic import BaseModel, Field

class ExecutionResult(BaseModel):
    """Represents the result of executing a code cell."""
    stdout: str = ""
    stderr: str = ""
    text_result: Optional[str] = None  # The return value representation
    images: List[str] = Field(default_factory=list)  # Base64 encoded images
    html: Optional[str] = None
    error: Optional[Dict[str, Any]] = None

    @property
    def is_success(self) -> bool:
        return self.error is None

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

    def save(self, path: str) -> None:
        """Save the notebook to disk."""
        ...
