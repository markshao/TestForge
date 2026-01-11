import pytest
from fastapi.testclient import TestClient
from forge.api.server import app
from forge.api.store import store

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def clean_store():
    # Clean up the store before each test
    store._tasks.clear()
    store._executions.clear()
    yield

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_task(client):
    payload = {
        "name": "Test Task",
        "description": "A test task",
        "yaml_content": "name: test\nsteps: []"
    }
    response = client.post("/api/v1/tasks", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]
    assert data["yaml_content"] == payload["yaml_content"]
    assert "id" in data
    assert data["status"] == "pending"

def test_list_tasks(client):
    # Create two tasks
    client.post("/api/v1/tasks", json={"name": "Task 1", "yaml_content": "..."})
    client.post("/api/v1/tasks", json={"name": "Task 2", "yaml_content": "..."})

    response = client.get("/api/v1/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    # Verify order (latest first)
    assert data[0]["name"] == "Task 2"
    assert data[1]["name"] == "Task 1"

def test_get_task(client):
    # Create a task
    create_res = client.post("/api/v1/tasks", json={"name": "Task 1", "yaml_content": "..."})
    task_id = create_res.json()["id"]

    # Get it
    response = client.get(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["id"] == task_id

    # Get non-existent
    response = client.get("/api/v1/tasks/non-existent")
    assert response.status_code == 404

def test_delete_task(client):
    # Create a task
    create_res = client.post("/api/v1/tasks", json={"name": "Task 1", "yaml_content": "..."})
    task_id = create_res.json()["id"]

    # Delete it
    response = client.delete(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 204

    # Verify it's gone
    response = client.get(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 404

def test_start_task(client):
    # Create a task
    create_res = client.post("/api/v1/tasks", json={"name": "Task 1", "yaml_content": "..."})
    task_id = create_res.json()["id"]

    # Start it
    response = client.post(f"/api/v1/tasks/{task_id}/start")
    assert response.status_code == 202
    assert response.json() == {"status": "accepted"}

    # Verify background task started (we can check status update)
    # Since background tasks run in thread pool, we might need a small sleep or check immediately
    # Note: TestClient runs background tasks synchronously after the response is sent
    
    # Check execution state
    response = client.get(f"/api/v1/tasks/{task_id}/execution")
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == task_id
    # It might be running or completed depending on how fast the background task ran
    assert data["status"] in ["running", "completed"] 
    assert len(data["logs"]) > 0

def test_get_execution_not_found(client):
    response = client.get("/api/v1/tasks/non-existent/execution")
    assert response.status_code == 404
