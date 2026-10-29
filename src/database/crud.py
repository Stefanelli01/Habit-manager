from database import get_db_connection
from datetime import date

def create_habit(name: str, description: str = ""):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO habit(name, description) VALUES(?, ?)",
            (name, description)
        )
        conn.commit()
        print(f"Habit '{name}' was created successfully")

    except Exception as e:
        print(e)

    finally:
        conn.close()



def get_all_habits():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM habits ORDER BY created_at DESC")
    habits = cursor.fetchall()

    conn.close()
    return habits



def mark_habit_completed(habit_id: int, completion_date: str = None):
    if completion_date is None:
        completion_date = str(date.today())

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO habit_logs (habit_id, completed_at) VALUES (?, ?)",
            (habit_id, completion_date)
        )
        conn.commit()
        print("Habit marked as completed!")

    except Exception as e:
        print(f"Could not log habit: {e}")

    finally:
        conn.close()
