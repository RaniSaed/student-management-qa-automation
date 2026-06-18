"""
Unit tests for app/db.py
- pymysql is mocked via pytest-mock — no real DB connection is made
- _get_connection is patched so every DB function uses a mock cursor
- Follows AAA pattern: Arrange / Act / Assert
- Each test is tagged with a Jira key
"""
import pytest
from unittest.mock import Mock

from app import db


# ---------------------------------------------------------------------------
# Shared fixture: patches _get_connection and returns (connection, cursor)
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_con(mocker):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_connection.cursor.return_value = mock_cursor
    mocker.patch("app.db._get_connection", return_value=mock_connection)
    return mock_connection, mock_cursor


# ---------------------------------------------------------------------------
# get_students
# ---------------------------------------------------------------------------

@pytest.mark.jira_key("STUDENT-101")
def test_get_students_returns_list(mock_con):
    # Arrange
    _, mock_cursor = mock_con
    expected = [
        {"id": 1, "name": "Alice", "age": 25},
        {"id": 2, "name": "Bob", "age": 30},
    ]
    mock_cursor.fetchall.return_value = expected

    # Act
    result = db.get_students()

    # Assert
    assert result == expected
    mock_cursor.execute.assert_called_once_with("select * from students")


# ---------------------------------------------------------------------------
# get_student
# ---------------------------------------------------------------------------

@pytest.mark.jira_key("STUDENT-102")
def test_get_student_returns_student(mock_con):
    # Arrange
    _, mock_cursor = mock_con
    mock_cursor.fetchone.return_value = {"id": 1, "name": "Alice", "age": 25}

    # Act
    result = db.get_student(1)

    # Assert
    assert result == {"id": 1, "name": "Alice", "age": 25}
    mock_cursor.execute.assert_called_once_with(
        "select * from students where id = %s", (1,)
    )


@pytest.mark.jira_key("STUDENT-103")
def test_get_student_not_found_raises_key_error(mock_con):
    # Arrange
    _, mock_cursor = mock_con
    mock_cursor.fetchone.return_value = None

    # Act / Assert
    with pytest.raises(KeyError, match="student not found: 999"):
        db.get_student(999)


# ---------------------------------------------------------------------------
# add_student
# ---------------------------------------------------------------------------

@pytest.mark.jira_key("STUDENT-104")
def test_add_student_returns_student_with_generated_id(mock_con):
    # Arrange
    mock_connection, mock_cursor = mock_con
    mock_cursor.lastrowid = 42

    # Act
    result = db.add_student({"name": "Alice", "age": 25})

    # Assert
    assert result["id"] == 42
    assert result["name"] == "Alice"
    assert result["age"] == 25
    mock_connection.commit.assert_called_once()


# ---------------------------------------------------------------------------
# update_student
# ---------------------------------------------------------------------------

@pytest.mark.jira_key("STUDENT-105")
def test_update_student_success(mocker):
    # Arrange
    mock_cursor = Mock()
    mock_cursor.rowcount = 1
    mock_connection = Mock()
    mock_connection.cursor.return_value = mock_cursor
    mocker.patch("app.db._get_connection", return_value=mock_connection)
    mocker.patch(
        "app.db.get_student",
        return_value={"id": 1, "name": "Alice Updated", "age": 30},
    )

    # Act
    result = db.update_student({"id": 1, "name": "Alice Updated", "age": 30})

    # Assert
    assert result == {"id": 1, "name": "Alice Updated", "age": 30}
    mock_connection.commit.assert_called_once()


@pytest.mark.jira_key("STUDENT-106")
def test_update_student_not_found_raises_key_error(mock_con):
    # Arrange
    _, mock_cursor = mock_con
    mock_cursor.rowcount = 0

    # Act / Assert
    with pytest.raises(KeyError):
        db.update_student({"id": 999, "name": "Ghost", "age": 25})


# ---------------------------------------------------------------------------
# delete_student
# ---------------------------------------------------------------------------

@pytest.mark.jira_key("STUDENT-107")
def test_delete_student_success(mocker):
    # Arrange
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_connection.cursor.return_value = mock_cursor
    mocker.patch("app.db._get_connection", return_value=mock_connection)
    mocker.patch(
        "app.db.get_student",
        return_value={"id": 1, "name": "Alice", "age": 25},
    )

    # Act
    result = db.delete_student(1)

    # Assert
    assert result == {"id": 1, "name": "Alice", "age": 25}
    mock_connection.commit.assert_called_once()


@pytest.mark.jira_key("STUDENT-108")
def test_delete_student_not_found_raises_key_error(mocker):
    # Arrange
    mocker.patch("app.db._get_connection")
    mocker.patch(
        "app.db.get_student",
        side_effect=KeyError("student not found: 999"),
    )

    # Act / Assert
    with pytest.raises(KeyError, match="student not found: 999"):
        db.delete_student(999)
