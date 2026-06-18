"""Integration tests for the Students API using the `requests` library.

These tests require the Flask server to be running at BASE_URL.
Start it with: python app/controller.py

The tests assume the students table exists and is empty at each run.
"""

import pytest
import requests

BASE_URL = "http://127.0.0.1:5000"
STUDENTS_ENDPOINT = f"{BASE_URL}/students"


@pytest.fixture(scope="module")
def base_url():
    """Return the base URL of the running server."""
    return BASE_URL


@pytest.fixture(autouse=True)
def cleanup_students(base_url):
    """Before each test, delete all students so we start clean."""
    resp = requests.get(f"{base_url}/students")
    if resp.status_code == 200:
        for student in resp.json():
            requests.delete(f"{base_url}/students/{student['id']}")
    yield


# -------- GET /students ----------

@pytest.mark.jira_key("SAQC-1")
def test_get_students_empty(base_url):
    """GET /students should return an empty list when no students exist."""
    resp = requests.get(f"{base_url}/students")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.jira_key("SAQC-1")
def test_get_students_with_data(base_url):
    """GET /students should return all students."""
    # add a student first
    requests.post(f"{base_url}/students", json={"name": "Test", "age": 20})
    resp = requests.get(f"{base_url}/students")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test"
    assert data[0]["age"] == 20


# -------- GET /students/<id> ----------

@pytest.mark.jira_key("SAQC-1")
def test_get_student_by_id(base_url):
    """GET /students/<id> should return the student."""
    post_resp = requests.post(f"{base_url}/students", json={"name": "Find Me", "age": 25})
    student_id = post_resp.json()["id"]

    resp = requests.get(f"{base_url}/students/{student_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Find Me"
    assert resp.json()["age"] == 25


@pytest.mark.jira_key("SAQC-1")
def test_get_student_not_found(base_url):
    """GET /students/<id> should return 404 for non-existent student."""
    resp = requests.get(f"{base_url}/students/9999")
    assert resp.status_code == 404
    assert "not found" in resp.json()["message"].lower()


# -------- POST /students ----------

@pytest.mark.jira_key("SAQC-1")
def test_add_student(base_url):
    """POST /students should create a new student and return 201."""
    resp = requests.post(f"{base_url}/students", json={"name": "New Student", "age": 22})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "New Student"
    assert data["age"] == 22
    assert "id" in data


@pytest.mark.jira_key("SAQC-1")
def test_add_student_underage(base_url):
    """POST /students with age < 18 should return 400."""
    resp = requests.post(f"{base_url}/students", json={"name": "Young", "age": 17})
    assert resp.status_code == 400
    assert "age" in resp.json()["message"].lower()


@pytest.mark.jira_key("SAQC-1")
def test_add_student_overage(base_url):
    """POST /students with age > 120 should return 400."""
    resp = requests.post(f"{base_url}/students", json={"name": "Old", "age": 150})
    assert resp.status_code == 400
    assert "age" in resp.json()["message"].lower()


@pytest.mark.jira_key("SAQC-1")
def test_add_student_empty_name(base_url):
    """POST /students with empty name should return 400."""
    resp = requests.post(f"{base_url}/students", json={"name": "", "age": 20})
    assert resp.status_code == 400
    assert "name" in resp.json()["message"].lower()


# -------- PUT /students ----------

@pytest.mark.jira_key("SAQC-1")
def test_update_student(base_url):
    """PUT /students should update an existing student."""
    # add a student first
    post_resp = requests.post(f"{base_url}/students", json={"name": "Before", "age": 20})
    student = post_resp.json()

    # update
    resp = requests.put(f"{base_url}/students", json={"id": student["id"], "name": "After", "age": 30})
    assert resp.status_code == 200
    assert resp.json()["name"] == "After"
    assert resp.json()["age"] == 30


@pytest.mark.jira_key("SAQC-1")
def test_update_student_not_found(base_url):
    """PUT /students for non-existent student should return 404."""
    resp = requests.put(f"{base_url}/students", json={"id": 9999, "name": "Ghost", "age": 20})
    assert resp.status_code == 404
    assert "not found" in resp.json()["message"].lower()


# -------- DELETE /students/<id> ----------

@pytest.mark.jira_key("SAQC-1")
def test_delete_student(base_url):
    """DELETE /students/<id> should delete the student."""
    # add a student first
    post_resp = requests.post(f"{base_url}/students", json={"name": "Delete Me", "age": 25})
    student_id = post_resp.json()["id"]

    # delete
    resp = requests.delete(f"{base_url}/students/{student_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Delete Me"

    # verify it's gone
    get_resp = requests.get(f"{base_url}/students/{student_id}")
    assert get_resp.status_code == 404


@pytest.mark.jira_key("SAQC-1")
def test_delete_student_not_found(base_url):
    """DELETE /students/<id> for non-existent student should return 404."""
    resp = requests.delete(f"{base_url}/students/9999")
    assert resp.status_code == 404
    assert "not found" in resp.json()["message"].lower()
