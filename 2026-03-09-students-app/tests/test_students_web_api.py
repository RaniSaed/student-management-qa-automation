"""
Step 2 — API Integration Tests
Sends real HTTP requests via `requests` to a live Flask server.
MySQL must be running and students_db must exist (run db/init_db.py once).
The server is started automatically by the `live_server` fixture in conftest.py.

Run:
    uv run pytest tests/test_students_web_api.py -v
"""
import pytest
import requests


# ---------------------------------------------------------------------------
# Fixture: creates a student before the test, deletes it after.
# Function-scoped → each test gets a fresh, isolated student.
# ---------------------------------------------------------------------------

@pytest.fixture
def created_student(live_server):
    response = requests.post(
        f"{live_server}/students",
        json={"name": "Integration Student", "age": 25},
    )
    assert response.status_code == 201, "Fixture: failed to create student"
    student = response.json()
    yield student
    requests.delete(f"{live_server}/students/{student['id']}")


# ---------------------------------------------------------------------------
# GET /students
# ---------------------------------------------------------------------------

@pytest.mark.jira_key("STUDENT-201")
def test_get_all_students_returns_200_and_list(live_server):
    # Arrange / Act
    response = requests.get(f"{live_server}/students")

    # Assert
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ---------------------------------------------------------------------------
# GET /students/<id>
# ---------------------------------------------------------------------------

@pytest.mark.jira_key("STUDENT-202")
def test_get_existing_student_returns_200(live_server, created_student):
    # Arrange
    student_id = created_student["id"]

    # Act
    response = requests.get(f"{live_server}/students/{student_id}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == student_id
    assert data["name"] == created_student["name"]
    assert data["age"] == created_student["age"]


@pytest.mark.jira_key("STUDENT-203")
def test_get_nonexistent_student_returns_404(live_server):
    # Act
    response = requests.get(f"{live_server}/students/999999")

    # Assert
    assert response.status_code == 404
    assert "message" in response.json()


# ---------------------------------------------------------------------------
# POST /students
# ---------------------------------------------------------------------------

@pytest.mark.jira_key("STUDENT-204")
def test_post_valid_student_returns_201_with_id(live_server):
    # Arrange
    payload = {"name": "New Student", "age": 22}

    # Act
    response = requests.post(f"{live_server}/students", json=payload)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Student"
    assert data["age"] == 22
    assert "id" in data

    # cleanup
    requests.delete(f"{live_server}/students/{data['id']}")


@pytest.mark.jira_key("STUDENT-205")
def test_post_student_age_below_18_returns_400(live_server):
    # Arrange
    payload = {"name": "Young Student", "age": 17}

    # Act
    response = requests.post(f"{live_server}/students", json=payload)

    # Assert
    assert response.status_code == 400
    assert "message" in response.json()


@pytest.mark.jira_key("STUDENT-206")
def test_post_student_age_above_120_returns_400(live_server):
    # Arrange
    payload = {"name": "Ancient Student", "age": 121}

    # Act
    response = requests.post(f"{live_server}/students", json=payload)

    # Assert
    assert response.status_code == 400
    assert "message" in response.json()


@pytest.mark.jira_key("STUDENT-207")
def test_post_student_empty_name_returns_400(live_server):
    # Arrange
    payload = {"name": "", "age": 25}

    # Act
    response = requests.post(f"{live_server}/students", json=payload)

    # Assert
    assert response.status_code == 400
    assert "message" in response.json()


# ---------------------------------------------------------------------------
# PUT /students
# ---------------------------------------------------------------------------

@pytest.mark.jira_key("STUDENT-208")
def test_put_valid_update_returns_200(live_server, created_student):
    # Arrange
    payload = {
        "id": created_student["id"],
        "name": "Updated Name",
        "age": 30,
    }

    # Act
    response = requests.put(f"{live_server}/students", json=payload)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["age"] == 30
    assert data["id"] == created_student["id"]


@pytest.mark.jira_key("STUDENT-209")
def test_put_nonexistent_student_returns_404(live_server):
    # Arrange
    payload = {"id": 999999, "name": "Ghost", "age": 25}

    # Act
    response = requests.put(f"{live_server}/students", json=payload)

    # Assert
    assert response.status_code == 404
    assert "message" in response.json()


# ---------------------------------------------------------------------------
# DELETE /students/<id>
# ---------------------------------------------------------------------------

@pytest.mark.jira_key("STUDENT-210")
def test_delete_existing_student_returns_200(live_server):
    # Arrange — create a dedicated student just to delete it
    student = requests.post(
        f"{live_server}/students",
        json={"name": "To Delete", "age": 20},
    ).json()

    # Act
    response = requests.delete(f"{live_server}/students/{student['id']}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == student["id"]
    assert data["name"] == "To Delete"


@pytest.mark.jira_key("STUDENT-211")
def test_delete_nonexistent_student_returns_404(live_server):
    # Act
    response = requests.delete(f"{live_server}/students/999999")

    # Assert
    assert response.status_code == 404
    assert "message" in response.json()
