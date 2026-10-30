from src.crud import create_habit, get_all_habits, mark_habit_completed
from src.database.database import get_db_connection, init_db
from src.streak import calculate_streak

def run_tests():

    print("Starting DB")
    init_db()

    print("\n2. Creating test habit")


    try:
        a = input("What is habit? ")
        b = input("What is description of habit? ")

        create_habit(a, b)

    except ValueError as e:
        print(e)

    print("\n3. Searching habits")

    habits = get_all_habits()

    print(f"Cadastred Habits: {[dict(h) for h in habits]}")

    if habits:
        habit_id = habits[0]["id"]

        print(f"\n4. Finishing habit: {habit_id}")

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
        print(f"\n5. History: {logs}")
        print(f"6. Streak: {streak} dia(s)")


if __name__ == "__main__":
    run_tests()