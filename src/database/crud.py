from database import get_db_connection

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