import asyncio
import queue
import time
from typing import Any, Dict, Optional
from jupyter_client.manager import KernelManager
from jupyter_client.blocking.client import BlockingKernelClient
from .interface import ExecutionResult, Kernel

class JupyterKernel(Kernel):
    """
    A concrete implementation of Kernel using jupyter_client.
    It manages a single Python kernel process.
    """

    def __init__(self, kernel_name: str = "python3"):
        self.kernel_name = kernel_name
        self._km: Optional[KernelManager] = None
        self._kc: Optional[BlockingKernelClient] = None

    def start(self) -> None:
        """Start the kernel process."""
        if self._km is not None:
            return  # Already started

        self._km = KernelManager(kernel_name=self.kernel_name)
        self._km.start_kernel()
        
        self._kc = self._km.client()
        self._kc.start_channels()
        
        # Wait for kernel to be ready
        try:
            self._kc.wait_for_ready(timeout=10)
        except RuntimeError:
            self.stop()
            raise RuntimeError("Kernel failed to start within timeout.")

    def stop(self) -> None:
        """Stop the kernel process."""
        if self._kc:
            self._kc.stop_channels()
            self._kc = None
        
        if self._km:
            self._km.shutdown_kernel(now=True)
            self._km = None

    def execute(self, code: str) -> ExecutionResult:
        """
        Execute code synchronously.
        NOTE: This blocks until execution finishes.
        """
        if not self._kc:
            raise RuntimeError("Kernel is not running. Call start() first.")

        # 1. Send execute request
        msg_id = self._kc.execute(code)

        # 2. Poll for messages until idle
        # We need to collect: stdout, stderr, display_data (images), execute_result
        stdout_parts = []
        stderr_parts = []
        images = []
        text_result = None
        error_info = None
        
        # Loop until we receive 'idle' status
        while True:
            try:
                # Get IOPub message (stdout, stderr, display, status)
                msg = self._kc.get_iopub_msg(timeout=30)
                msg_type = msg["header"]["msg_type"]
                content = msg["content"]
                
                # Check for parent_header to match our request
                if msg["parent_header"].get("msg_id") != msg_id:
                    continue

                if msg_type == "stream":
                    if content["name"] == "stdout":
                        stdout_parts.append(content["text"])
                    elif content["name"] == "stderr":
                        stderr_parts.append(content["text"])
                
                elif msg_type == "execute_result":
                    text_result = content["data"].get("text/plain")
                
                elif msg_type == "display_data":
                    data = content["data"]
                    if "image/png" in data:
                        images.append(data["image/png"])
                    elif "text/plain" in data:
                        # Some libraries use display_data for text output too
                        stdout_parts.append(data["text/plain"])

                elif msg_type == "error":
                    error_info = {
                        "ename": content["ename"],
                        "evalue": content["evalue"],
                        "traceback": content["traceback"]
                    }

                elif msg_type == "status":
                    if content["execution_state"] == "idle":
                        break
            
            except queue.Empty:
                # Timeout waiting for message
                error_info = {"ename": "TimeoutError", "evalue": "Execution timed out", "traceback": []}
                break
            except Exception as e:
                error_info = {"ename": type(e).__name__, "evalue": str(e), "traceback": []}
                break

        return ExecutionResult(
            stdout="".join(stdout_parts),
            stderr="".join(stderr_parts),
            text_result=text_result,
            images=images,
            error=error_info
        )

    async def aexecute(self, code: str) -> ExecutionResult:
        """Execute code asynchronously by running the synchronous execute in a thread."""
        return await asyncio.to_thread(self.execute, code)
