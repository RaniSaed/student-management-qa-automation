"""
Unit tests for app/service.py
- All DB calls are mocked via pytest-mock (no real DB connection)
- Follows AAA pattern: Arrange / Act / Assert
- Each test is tagged with a Jira key
"""
import pytest

from app import service
from app.service import ServiceError


# ---------------------------------------------------------------------------
# get_student
# ---------------------------------------------------------------------------

@pytest.mark.jira_key("STUDENT-001")
def test_get_student_returns_student(mocker):
    # Arrange
    mock_db = mocker.patch("app.service.db.get_student")
    mock_db.return_value = {"id": 1, "name": "Alice", "age": 25}

    # Act
    result = service.get_student(1)

    # Assert
    assert result == {"id": 1, "name": "Alice", "age": 25}
    mock_db.assert_called_once_with(1)


@pytest.mark.jira_key("STUDENT-002")
def test_get_student_not_found_raises_key_error(mocker):
    # Arrange
    mock_db = mocker.patch("app.service.db.get_student")
    mock_db.side_effect = KeyError("student not found: 999")

    # Act / Assert
    with pytest.raises(KeyError):
        service.get_student(999)

    mock_db.assert_called_once_with(999)


# ---------------------------------------------------------------------------
# add_student
# ---------------------------------------------------------------------------

@pytest.mark.jira_key("STUDENT-003")
def test_add_student_valid_min_age(mocker):
    # Arrange
    mock_db = mocker.patch("app.service.db.add_student")
    mock_db.return_value = {"id": 1, "name": "Alice", "age": 18}

    # Act
    result = service.add_student({"name": "Alice", "age": 18})

    # Assert
    assert result == {"id": 1, "name": "Alice", "age": 18}
    mock_db.assert_called_once()


@pytest.mark.jira_key("STUDENT-004")
def test_add_student_valid_max_age(mocker):
    # Arrange
    mock_db = mocker.patch("app.service.db.add_student")
    mock_db.return_value = {"id": 2, "name": "Bob", "age": 120}

    # Act
    result = service.add_student({"name": "Bob", "age": 120})

    # Assert
    assert result == {"id": 2, "name": "Bob", "age": 120}
    mock_db.assert_called_once()


@pytest.mark.jira_key("STUDENT-005")
def test_add_student_age_below_18_raises_service_error(mocker):
    # Arrange
    mock_db = mocker.patch("app.service.db.add_student")

    # Act / Assert
    with pytest.raises(ServiceError):
        service.add_student({"name": "Alice", "age": 17})

    mock_db.assert_not_called()


@pytest.mark.jira_key("STUDENT-006")
def test_add_student_age_above_120_raises_service_error(mocker):
    # Arrange
    mock_db = mocker.patch("app.service.db.add_student")

    # Act / Assert
    with pytest.raises(ServiceError):
        service.add_student({"name": "Alice", "age": 121})

    mock_db.assert_not_called()


@pytest.mark.jira_key("STUDENT-007")
def test_add_student_empty_name_raises_service_error(mocker):
    # Arrange
    mock_db = mocker.patch("app.service.db.add_student")

    # Act / Assert
    with pytest.raises(ServiceError):
        service.add_student({"name": "", "age": 25})

    mock_db.assert_not_called()


# ---------------------------------------------------------------------------
# update_student
# ---------------------------------------------------------------------------

@pytest.mark.jira_key("STUDENT-008")
def test_update_student_valid(mocker):
    # Arrange
    mock_db = mocker.patch("app.service.db.update_student")
    mock_db.return_value = {"id": 1, "name": "Alice Updated", "age": 30}

    # Act
    result = service.update_student({"id": 1, "name": "Alice Updated", "age": 30})

    # Assert
    assert result == {"id": 1, "name": "Alice Updated", "age": 30}
    mock_db.assert_called_once()


@pytest.mark.jira_key("STUDENT-009")
def test_update_student_not_found_raises_key_error(mocker):
    # Arrange
    mock_db = mocker.patch("app.service.db.update_student")
    mock_db.side_effect = KeyError("student not found: 999")

    # Act / Assert
    with pytest.raises(KeyError):
        service.update_student({"id": 999, "name": "Ghost", "age": 25})

    mock_db.assert_called_once()


# ---------------------------------------------------------------------------
# delete_student
# ---------------------------------------------------------------------------

@pytest.mark.jira_key("STUDENT-010")
def test_delete_student_valid(mocker):
    # Arrange
    mock_db = mocker.patch("app.service.db.delete_student")
    mock_db.return_value = {"id": 1, "name": "Alice", "age": 25}

    # Act
    result = service.delete_student(1)

    # Assert
    assert result == {"id": 1, "name": "Alice", "age": 25}
    mock_db.assert_called_once_with(1)


@pytest.mark.jira_key("STUDENT-011")
def test_delete_student_not_found_raises_key_error(mocker):
    # Arrange
    mock_db = mocker.patch("app.service.db.delete_student")
    mock_db.side_effect = KeyError("student not found: 999")

    # Act / Assert
    with pytest.raises(KeyError):
        service.delete_student(999)

    mock_db.assert_called_once_with(999)
