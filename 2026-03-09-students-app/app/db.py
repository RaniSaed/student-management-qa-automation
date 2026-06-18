import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "students_db"),
    "cursorclass": pymysql.cursors.DictCursor,
}


# a function to get connection to the database
def _get_connection() -> pymysql.Connection:
    con = pymysql.connect(**DB_CONFIG)
    return con


def get_students():
    con = _get_connection()
    try:
        cursor = con.cursor()
        cursor.execute("select * from students")
        return cursor.fetchall()
    finally:
        con.close()


def get_student(student_id):
    con = _get_connection()
    try:
        cursor = con.cursor()
        cursor.execute("select * from students where id = %s", (student_id,))
        student = cursor.fetchone()
        if student is None:
            raise KeyError(f"student not found: {student_id}")
        return student
    finally:
        con.close()


def add_student(student):
    con = _get_connection()
    try:
        cursor = con.cursor()
        cursor.execute("insert into students (name, age) values (%s, %s)", (student["name"], student["age"]))
        con.commit()
        the_generated_id = cursor.lastrowid
        student["id"] = the_generated_id
        return student
    finally:
        con.close()


def update_student(student):
    con = _get_connection()
    try:
        cursor = con.cursor()
        cursor.execute("update students set name=%s, age=%s where id=%s",
                       (student["name"], student["age"], student["id"]))
        if cursor.rowcount == 0:
            raise KeyError(f'student not found: {student["id"]}')
        con.commit()
        return get_student(student["id"])
    finally:
        con.close()


def delete_student(student_id):
    con = _get_connection()
    student = get_student(student_id)
    try:
        cursor = con.cursor()
        cursor.execute("delete from students where id = %s", (student_id,))
        con.commit()
        return student
    finally:
        con.close()
