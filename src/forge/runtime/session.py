import nbformat
from typing import Any, Dict
from .interface import ExecutionResult, NotebookSession
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
        # 1. Execute the code
        result = await self.kernel.aexecute(code)

        # 2. Create a notebook cell
        cell = nbformat.v4.new_code_cell(source=code)
        
        # 3. Populate outputs
        outputs = []
        
        if result.stdout:
            outputs.append(nbformat.v4.new_output(
                output_type="stream",
                name="stdout",
                text=result.stdout
            ))
            
        if result.stderr:
            outputs.append(nbformat.v4.new_output(
                output_type="stream",
                name="stderr",
                text=result.stderr
            ))
            
        if result.text_result:
            outputs.append(nbformat.v4.new_output(
                output_type="execute_result",
                data={"text/plain": result.text_result}
            ))
            
        for img_base64 in result.images:
            outputs.append(nbformat.v4.new_output(
                output_type="display_data",
                data={"image/png": img_base64}
            ))
            
        if result.error:
            outputs.append(nbformat.v4.new_output(
                output_type="error",
                ename=result.error["ename"],
                evalue=result.error["evalue"],
                traceback=result.error["traceback"]
            ))

        cell.outputs = outputs
        self.notebook.cells.append(cell)
        
        return result

    def get_notebook_json(self) -> Dict[str, Any]:
        """Return the current state of the notebook in nbformat JSON."""
        return dict(self.notebook)

    def save(self, path: str) -> None:
        """Save the notebook to disk."""
        with open(path, "w", encoding="utf-8") as f:
            nbformat.write(self.notebook, f)
