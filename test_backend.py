from src.database.crud import create_habit, get_all_habits, mark_habit_completed
from src.database.database import get_db_connection, init_db
from src.streak import calculate_streak


def run_tests():
    init_db()
    create_habit("Read Books", "Read 10 pages daily")
    habits = get_all_habits()

    if habits:
        habit_id = habits[0]["id"]
        mark_habit_completed(habit_id)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT completed_at FROM habit_logs WHERE habit_id = ? ORDER BY completed_at DESC",
            (habit_id,),
        )
        logs = [row["completed_at"] for row in cursor.fetchall()]
        conn.close()

        streak = calculate_streak(logs)
        print(f"Habit ID {habit_id} current streak: {streak}")


if __name__ == "__main__":
    run_tests()