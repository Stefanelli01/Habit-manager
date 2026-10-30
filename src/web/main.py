import os
from contextlib import asynccontextmanager
from datetime import date
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.database.crud import create_habit, get_all_habits, mark_habit_completed
from src.database.database import get_db_connection, init_db
from src.streak import calculate_streak


@asynccontextmanager
async def lifespan(app: FastAPI):
    static_dir = "src/web/static"
    os.makedirs(static_dir, exist_ok=True)
    init_db()
    yield


app = FastAPI(title="Habit Manager", lifespan=lifespan)

templates = Jinja2Templates(directory="src/web/templates")
app.mount("/static", StaticFiles(directory="src/web/static"), name="static")


def fetch_habits_with_streaks():
    habits = get_all_habits()
    habits_list = []
    today_str = str(date.today())

    conn = get_db_connection()
    cursor = conn.cursor()

    for habit in habits:
        habit_dict = dict(habit)
        cursor.execute(
            "SELECT completed_at FROM habit_logs WHERE habit_id = ? ORDER BY completed_at DESC",
            (habit_dict["id"],),
        )
        logs = [row["completed_at"] for row in cursor.fetchall()]

        habit_dict["streak"] = calculate_streak(logs)
        habit_dict["completed_today"] = today_str in logs
        habits_list.append(habit_dict)

    conn.close()
    return habits_list


@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    habits = fetch_habits_with_streaks()
    return templates.TemplateResponse(
        request=request, name="index.html", context={"habits": habits}
    )


@app.post("/habits", response_class=HTMLResponse)
async def add_habit(
    request: Request, name: str = Form(...), description: str = Form("")
):
    if name.strip():
        create_habit(name.strip(), description.strip())

    habits = fetch_habits_with_streaks()
    return templates.TemplateResponse(
        request=request,
        name="partials/habit_list.html",
        context={"habits": habits},
    )


@app.post("/habits/{habit_id}/complete", response_class=HTMLResponse)
async def complete_habit(request: Request, habit_id: int):
    mark_habit_completed(habit_id)
    habits = fetch_habits_with_streaks()
    return templates.TemplateResponse(
        request=request,
        name="partials/habit_list.html",
        context={"habits": habits},
    )