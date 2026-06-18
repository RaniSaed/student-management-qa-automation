"""
Run this script once to create the database and students table.
Safe to run multiple times — uses IF NOT EXISTS everywhere.

Usage:
    uv run python db/init_db.py
"""
import os
import sys

import pymysql
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "students_db")


def init_db():
    try:
        con = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            cursorclass=pymysql.cursors.DictCursor,
        )
    except pymysql.err.OperationalError as e:
        print(f"ERROR: Could not connect to MySQL at {DB_HOST} as '{DB_USER}'.")
        print(f"       {e}")
        print("\nMake sure MySQL is running and your .env credentials are correct.")
        sys.exit(1)

    try:
        with con.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
                f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            cursor.execute(f"USE `{DB_NAME}`")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id   INT          AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    age  INT          NOT NULL
                )
            """)
            con.commit()
        print(f"[OK] Database '{DB_NAME}' is ready.")
        print(f"[OK] Table 'students' is ready.")
    finally:
        con.close()


if __name__ == "__main__":
    init_db()
