import nbformat
from typing import Any, Dict
from .interface import ExecutionResult, NotebookSession, Cell, CellStatus, NotebookState
from .kernel import JupyterKernel

class JupyterNotebookSession(NotebookSession):
    """
    A session that manages a Jupyter Notebook and its associated Kernel.
    """

    def __init__(self, name: str = "notebook"):
        self.name = name
        self.kernel = JupyterKernel()
        # Initialize an empty notebook (v4)
        self.notebook = nbformat.v4.new_notebook()
        self.notebook.metadata.kernelspec = {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        }

    def start(self) -> None:
        """Start the session and the underlying kernel."""
        self.kernel.start()

    def stop(self) -> None:
        """Stop the session and the underlying kernel."""
        self.kernel.stop()

    async def add_cell(self, code: str) -> ExecutionResult:
        """Add a cell, execute it, and record the result asynchronously."""
        # 1. Create a notebook cell with RUNNING status
        cell = nbformat.v4.new_code_cell(source=code)
        # Store status in metadata so we can retrieve it later
        cell.metadata["status"] = CellStatus.RUNNING
        self.notebook.cells.append(cell)

        try:
            # 2. Execute the code
            result = await self.kernel.aexecute(code)
            
            # 3. Populate outputs directly from ExecutionResult
            # Since ExecutionResult.outputs is already a list of nbformat-compliant dicts
            
            # Convert plain dicts to nbformat nodes for consistency, 
            # though simple dict assignment often works in many tools.
            # nbformat.from_dict handles validation better.
            cell.outputs = [nbformat.from_dict(out) for out in result.outputs]

            if result.is_success:
                cell.metadata["status"] = CellStatus.SUCCESS
            else:
                cell.metadata["status"] = CellStatus.ERROR

            return result
        except Exception:
            cell.metadata["status"] = CellStatus.ERROR
            raise

    def get_notebook_json(self) -> Dict[str, Any]:
        """Return the current state of the notebook in nbformat JSON."""
        return dict(self.notebook)

    def get_state(self) -> NotebookState:
        """Return the current state of the notebook for UI rendering."""
        cells = []
        for nb_cell in self.notebook.cells:
            status = nb_cell.metadata.get("status", CellStatus.PENDING)
            cells.append(Cell(
                id=nb_cell.id,
                source=nb_cell.source,
                status=status,
                outputs=nb_cell.outputs,
                execution_count=nb_cell.execution_count
            ))
        return NotebookState(cells=cells)

    def save(self, path: str) -> None:
        """Save the notebook to disk."""
        with open(path, "w", encoding="utf-8") as f:
            nbformat.write(self.notebook, f)
