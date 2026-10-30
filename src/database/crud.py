from datetime import date
from src.database.database import get_db_connection


def create_habit(name: str, description: str = "") -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO habits (name, description) VALUES (?, ?)",
            (name, description),
        )
        conn.commit()
    finally:
        conn.close()


def get_all_habits() -> list:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM habits ORDER BY created_at DESC")
    habits = cursor.fetchall()
    conn.close()
    return habits


def mark_habit_completed(habit_id: int, completion_date: str = None) -> None:
    if completion_date is None:
        completion_date = str(date.today())

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO habit_logs (habit_id, completed_at) VALUES (?, ?)",
            (habit_id, completion_date),
        )
        conn.commit()
    finally:
        conn.close()