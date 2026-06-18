"""Unit tests for service.py using mocking - tests business logic in isolation from DB."""

from unittest.mock import patch, Mock
import pytest

from app import service
from app.service import ServiceError


# -------- get_student ----------

@pytest.mark.jira_key("SAQC-1")
@patch("app.service.db.get_student")
def test_get_student_positive(mock_get_student):
    """Should return the student when found."""
    mock_get_student.return_value = {"id": 1, "name": "John", "age": 22}
    result = service.get_student(1)
    assert result["id"] == 1
    assert result["name"] == "John"
    assert result["age"] == 22
    mock_get_student.assert_called_once_with(1)


@pytest.mark.jira_key("SAQC-1")
@patch("app.service.db.get_student")
def test_get_student_not_found(mock_get_student):
    """Should propagate KeyError when student not found."""
    mock_get_student.side_effect = KeyError("student not found: 999")
    with pytest.raises(KeyError, match="student not found: 999"):
        service.get_student(999)
    mock_get_student.assert_called_once_with(999)


# -------- get_students ----------

@pytest.mark.jira_key("SAQC-1")
@patch("app.service.db.get_students")
def test_get_students_positive(mock_get_students):
    """Should return list of all students."""
    mock_get_students.return_value = [
        {"id": 1, "name": "Alice", "age": 22},
        {"id": 2, "name": "Bob", "age": 25},
    ]
    result = service.get_students()
    assert len(result) == 2
    assert result[0]["name"] == "Alice"
    mock_get_students.assert_called_once()


# -------- add_student ----------

@pytest.mark.jira_key("SAQC-1")
@patch("app.service.db.add_student")
def test_add_student_positive(mock_add_student):
    """Should add a valid student and return with generated ID."""
    mock_add_student.return_value = {"id": 101, "name": "Charlie", "age": 25}
    result = service.add_student({"name": "Charlie", "age": 25})
    assert result["id"] == 101
    assert result["name"] == "Charlie"
    assert result["age"] == 25
    mock_add_student.assert_called_once_with({"name": "Charlie", "age": 25})


@pytest.mark.jira_key("SAQC-1")
@patch("app.service.db.add_student")
def test_add_student_min_age(mock_add_student):
    """Should allow adding a student with minimum age (18)."""
    mock_add_student.return_value = {"id": 1, "name": "Young", "age": 18}
    result = service.add_student({"name": "Young", "age": 18})
    assert result["age"] == 18


@pytest.mark.jira_key("SAQC-1")
@patch("app.service.db.add_student")
def test_add_student_max_age(mock_add_student):
    """Should allow adding a student with maximum age (120)."""
    mock_add_student.return_value = {"id": 1, "name": "Old", "age": 120}
    result = service.add_student({"name": "Old", "age": 120})
    assert result["age"] == 120


@pytest.mark.jira_key("SAQC-1")
@patch("app.service.db.add_student")
def test_add_student_too_young(mock_add_student):
    """Should reject a student under 18."""
    with pytest.raises(ServiceError, match="Student age is illegal: 17"):
        service.add_student({"name": "Too Young", "age": 17})
    mock_add_student.assert_not_called()


@pytest.mark.jira_key("SAQC-1")
@patch("app.service.db.add_student")
def test_add_student_too_old(mock_add_student):
    """Should reject a student over 120."""
    with pytest.raises(ServiceError, match="Student age is illegal: 121"):
        service.add_student({"name": "Too Old", "age": 121})
    mock_add_student.assert_not_called()


@pytest.mark.jira_key("SAQC-1")
@patch("app.service.db.add_student")
def test_add_student_empty_name(mock_add_student):
    """Should reject a student with empty name."""
    with pytest.raises(ServiceError, match="Student name is illegal"):
        service.add_student({"name": "", "age": 20})
    mock_add_student.assert_not_called()


@pytest.mark.jira_key("SAQC-1")
@patch("app.service.db.add_student")
def test_add_student_none_name(mock_add_student):
    """Should reject a student with None name."""
    with pytest.raises(ServiceError, match="Student name is illegal"):
        service.add_student({"name": None, "age": 20})
    mock_add_student.assert_not_called()


# -------- update_student ----------

@pytest.mark.jira_key("SAQC-1")
@patch("app.service.db.update_student")
def test_update_student_positive(mock_update_student):
    """Should update an existing student with valid data."""
    mock_update_student.return_value = {"id": 1, "name": "Updated", "age": 30}
    result = service.update_student({"id": 1, "name": "Updated", "age": 30})
    assert result["name"] == "Updated"
    assert result["age"] == 30
    mock_update_student.assert_called_once_with({"id": 1, "name": "Updated", "age": 30})


@pytest.mark.jira_key("SAQC-1")
@patch("app.service.db.update_student")
def test_update_student_not_found(mock_update_student):
    """Should propagate KeyError when updating non-existent student."""
    mock_update_student.side_effect = KeyError("student not found: 999")
    with pytest.raises(KeyError, match="student not found: 999"):
        service.update_student({"id": 999, "name": "Ghost", "age": 20})


@pytest.mark.jira_key("SAQC-1")
@patch("app.service.db.update_student")
def test_update_student_invalid_age(mock_update_student):
    """Should reject update when new age is invalid."""
    with pytest.raises(ServiceError, match="Student age is illegal: 15"):
        service.update_student({"id": 1, "name": "Bad", "age": 15})
    mock_update_student.assert_not_called()


# -------- delete_student ----------

@pytest.mark.jira_key("SAQC-1")
@patch("app.service.db.delete_student")
def test_delete_student_positive(mock_delete_student):
    """Should delete and return the deleted student."""
    mock_delete_student.return_value = {"id": 1, "name": "To Delete", "age": 22}
    result = service.delete_student(1)
    assert result["id"] == 1
    mock_delete_student.assert_called_once_with(1)


@pytest.mark.jira_key("SAQC-1")
@patch("app.service.db.delete_student")
def test_delete_student_not_found(mock_delete_student):
    """Should propagate KeyError when deleting non-existent student."""
    mock_delete_student.side_effect = KeyError("student not found: 999")
    with pytest.raises(KeyError, match="student not found: 999"):
        service.delete_student(999)
