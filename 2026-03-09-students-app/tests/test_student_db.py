"""Unit tests for db.py using mocking - no real MySQL needed."""

from unittest.mock import patch, MagicMock, call
import pytest

# We'll import after applying patches
import app.db as db


@pytest.fixture
def mock_cursor():
    """Fixture that returns a mock cursor object."""
    cursor = MagicMock()
    cursor.fetchall.return_value = [
        {"id": 1, "name": "Alice", "age": 22},
        {"id": 2, "name": "Bob", "age": 25},
    ]
    cursor.fetchone.return_value = {"id": 1, "name": "Alice", "age": 22}
    cursor.lastrowid = 101
    cursor.rowcount = 1
    return cursor


@pytest.fixture
def mock_connection(mock_cursor):
    """Fixture that patches _get_connection and returns a mock connection."""
    con = MagicMock()
    con.cursor.return_value = mock_cursor

    with patch.object(db, "_get_connection", return_value=con) as mock_get_con:
        yield mock_get_con


@pytest.mark.jira_key("SAQC-1")
def test_get_students_returns_list(mock_connection):
    """get_students should return all students from the DB."""
    students = db.get_students()
    assert len(students) == 2
    assert students[0]["name"] == "Alice"
    assert students[1]["age"] == 25


@pytest.mark.jira_key("SAQC-1")
def test_get_student_found(mock_connection):
    """get_student should return the correct student when found."""
    student = db.get_student(1)
    assert student["id"] == 1
    assert student["name"] == "Alice"
    assert student["age"] == 22


@pytest.mark.jira_key("SAQC-1")
def test_get_student_not_found():
    """get_student should raise KeyError when student doesn't exist."""
    cursor = MagicMock()
    cursor.fetchone.return_value = None
    con = MagicMock()
    con.cursor.return_value = cursor

    with patch.object(db, "_get_connection", return_value=con):
        with pytest.raises(KeyError, match="student not found: 999"):
            db.get_student(999)


@pytest.mark.jira_key("SAQC-1")
def test_add_student_success(mock_connection, mock_cursor):
    """add_student should insert and return the student with generated ID."""
    result = db.add_student({"name": "Charlie", "age": 30})

    # verify insert was called
    mock_cursor.execute.assert_called_once_with(
        "insert into students (name, age) values (%s, %s)",
        ("Charlie", 30),
    )
    assert result["id"] == 101
    assert result["name"] == "Charlie"
    assert result["age"] == 30


@pytest.mark.jira_key("SAQC-1")
def test_update_student_success():
    """update_student should update and return the updated student."""
    cursor = MagicMock()
    cursor.lastrowid = 101
    cursor.rowcount = 1
    # fetchone returns original data first (via get_student after update),
    # but we want it to return post-update data
    cursor.fetchone.return_value = {"id": 1, "name": "Alice Updated", "age": 23}

    con = MagicMock()
    con.cursor.return_value = cursor

    with patch.object(db, "_get_connection", return_value=con):
        result = db.update_student({"id": 1, "name": "Alice Updated", "age": 23})

    cursor.execute.assert_has_calls([
        call("update students set name=%s, age=%s where id=%s",
             ("Alice Updated", 23, 1)),
        call("select * from students where id = %s", (1,)),
    ])
    assert result["name"] == "Alice Updated"
    assert result["age"] == 23


@pytest.mark.jira_key("SAQC-1")
def test_update_student_not_found():
    """update_student should raise KeyError when student not found."""
    cursor = MagicMock()
    cursor.rowcount = 0  # no rows updated
    con = MagicMock()
    con.cursor.return_value = cursor

    with patch.object(db, "_get_connection", return_value=con):
        with pytest.raises(KeyError, match="student not found: 1"):
            db.update_student({"id": 1, "name": "X", "age": 20})


@pytest.mark.jira_key("SAQC-1")
def test_delete_student_success(mock_connection, mock_cursor):
    """delete_student should delete and return the deleted student."""
    result = db.delete_student(1)

    mock_cursor.execute.assert_has_calls([
        call("select * from students where id = %s", (1,)),
        call("delete from students where id = %s", (1,)),
    ])
    assert result["id"] == 1
    assert result["name"] == "Alice"
