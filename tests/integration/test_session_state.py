import pytest
import asyncio
from forge.runtime.session import JupyterNotebookSession
from forge.runtime.interface import CellStatus

@pytest.fixture
def session():
    s = JupyterNotebookSession()
    s.start()
    yield s
    s.stop()

@pytest.mark.asyncio
async def test_session_state_tracking(session):
    # This test simulates a long-running cell execution to verify state transitions
    # Since add_cell is awaitable, we can't easily poll state *while* it's running 
    # in a single-threaded test without creating a background task for execution.
    
    # 1. Define a long running task
    long_running_code = "import time; time.sleep(1); print('done')"
    
    # 2. Start execution in background task
    task = asyncio.create_task(session.add_cell(long_running_code))
    
    # 3. Give it a tiny moment to start
    await asyncio.sleep(0.1)
    
    # 4. Check state -> Should be RUNNING
    state = session.get_state()
    assert len(state.cells) == 1
    assert state.cells[0].status == CellStatus.RUNNING
    assert state.cells[0].source == long_running_code
    
    # 5. Wait for completion
    await task
    
    # 6. Check state -> Should be SUCCESS
    state = session.get_state()
    assert len(state.cells) == 1
    assert state.cells[0].status == CellStatus.SUCCESS
    assert state.cells[0].outputs[0]['text'] == "done\n"

@pytest.mark.asyncio
async def test_session_error_state(session):
    error_code = "raise ValueError('fail')"
    await session.add_cell(error_code)
    
    state = session.get_state()
    assert len(state.cells) == 1
    assert state.cells[0].status == CellStatus.ERROR
    assert state.cells[0].outputs[0]['ename'] == "ValueError"
