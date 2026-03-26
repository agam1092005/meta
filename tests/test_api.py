import pytest

def test_get_tasks(api_client):
    response = api_client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert len(data["tasks"]) == 3
    assert data["tasks"][0]["id"] == "easy"

def test_reset(api_client):
    response = api_client.post("/reset", json={"task_level": "medium"})
    assert response.status_code == 200
    data = response.json()
    assert "files_in_directory" in data
    # Check that we have at least some files from the medium template
    files = data["files_in_directory"]
    assert len(files) > 0
    assert any(f in files for f in ["build.sh", "app.py", "requirements.txt"])

def test_step_read(api_client):
    api_client.post("/reset", json={"task_level": "easy"})
    response = api_client.post("/step", json={
        "tool": "read_file",
        "file_path": "requirements.txt"
    })
    assert response.status_code == 200
    assert "Flsk" in response.json()["terminal_output"]

def test_grader_endpoint(api_client):
    api_client.post("/reset", json={"task_level": "easy"})
    response = api_client.get("/grader")
    assert response.status_code == 200
    assert "score" in response.json()
