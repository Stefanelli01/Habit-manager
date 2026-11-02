import hashlib
from datetime import date
from src.database.database import get_db_connection


def hash_password(password: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode(), b"habit_manager_salt", 100000
    ).hex()


def create_user(username: str, password: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username.strip(), hash_password(password)),
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def authenticate_user(username: str, password: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, password_hash FROM users WHERE username = ?",
        (username.strip(),),
    )
    user = cursor.fetchone()
    conn.close()

    if user and user["password_hash"] == hash_password(password):
        return dict(user)
    return None


def create_habit(user_id: int, name: str, description: str = "") -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO habits (user_id, name, description) VALUES (?, ?, ?)",
            (user_id, name, description),
        )
        conn.commit()
    finally:
        conn.close()


def get_all_habits_by_user(user_id: int) -> list:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM habits WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,),
    )
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


def delete_habit(user_id: int, habit_id: int) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM habits WHERE id = ? AND user_id = ?",
            (habit_id, user_id),
        )
        conn.commit()
    finally:
        conn.close()