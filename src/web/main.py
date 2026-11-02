import os
from contextlib import asynccontextmanager
from datetime import date, timedelta
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.database.crud import (
    authenticate_user,
    create_habit,
    create_user,
    delete_habit,
    get_all_habits_by_user,
    toggle_habit_completed,
)
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

PALETTES = [
    {"bg": "#10b981", "icon_bg": "rgba(16, 185, 129, 0.15)"},
    {"bg": "#059669", "icon_bg": "rgba(5, 150, 105, 0.15)"},
    {"bg": "#34d399", "icon_bg": "rgba(52, 211, 153, 0.15)"},
    {"bg": "#14b8a6", "icon_bg": "rgba(20, 184, 166, 0.15)"},
    {"bg": "#065f46", "icon_bg": "rgba(6, 95, 70, 0.2)"},
    {"bg": "#10b981", "icon_bg": "rgba(16, 185, 129, 0.15)"},
]


def get_current_user_id(request: Request):
    user_id = request.cookies.get("user_id")
    return int(user_id) if user_id and user_id.isdigit() else None


def fetch_habits_with_grid(user_id: int):
    habits = get_all_habits_by_user(user_id)
    today = date.today()
    days_strip = [(today - timedelta(days=i)) for i in range(6, -1, -1)]

    conn = get_db_connection()
    cursor = conn.cursor()

    habits_list = []
    for idx, habit in enumerate(habits):
        habit_dict = dict(habit)

        cursor.execute(
            "SELECT completed_at FROM habit_logs WHERE habit_id = ? ORDER BY completed_at DESC",
            (habit_dict["id"],),
        )
        logs = set(row["completed_at"] for row in cursor.fetchall())

        color_theme = PALETTES[idx % len(PALETTES)]
        habit_dict["color"] = color_theme["bg"]
        habit_dict["icon_bg"] = color_theme["icon_bg"]

        grid_days = []
        for d in days_strip:
            d_str = str(d)
            grid_days.append(
                {
                    "date": d_str,
                    "is_today": d == today,
                    "completed": d_str in logs,
                }
            )

        habit_dict["grid_days"] = grid_days
        habit_dict["streak"] = calculate_streak(sorted(list(logs), reverse=True))
        habits_list.append(habit_dict)

    conn.close()
    return habits_list, days_strip


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html", context={})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html", context={})


@app.post("/login")
async def login_submit(
    username: str = Form(...),
    password: str = Form(...),
    remember_me: str = Form(None),
):
    user = authenticate_user(username, password)
    if user:
        response = RedirectResponse(url="/", status_code=303)
        max_age = 30 * 24 * 60 * 60 if remember_me else None
        response.set_cookie(key="user_id", value=str(user["id"]), max_age=max_age)
        return response
    return RedirectResponse(url="/login?error=1", status_code=303)


@app.post("/register")
async def register_submit(
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    if password != confirm_password:
        return RedirectResponse(url="/register?error=mismatch", status_code=303)

    if create_user(username, password):
        user = authenticate_user(username, password)
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(key="user_id", value=str(user["id"]))
        return response

    return RedirectResponse(url="/register?error=exists", status_code=303)


@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key="user_id")
    return response


@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    user_id = get_current_user_id(request)
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    habits, days_strip = fetch_habits_with_grid(user_id)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"habits": habits, "days_strip": days_strip},
    )


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    user_id = get_current_user_id(request)
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse(
        request=request, name="settings.html", context={}
    )


@app.post("/habits", response_class=HTMLResponse)
async def add_habit(
    request: Request, name: str = Form(...), description: str = Form("")
):
    user_id = get_current_user_id(request)
    if user_id and name.strip():
        create_habit(user_id, name.strip(), description.strip())

    habits, days_strip = fetch_habits_with_grid(user_id)
    return templates.TemplateResponse(
        request=request,
        name="partials/habit_list.html",
        context={"habits": habits, "days_strip": days_strip},
    )


@app.post("/habits/{habit_id}/complete", response_class=HTMLResponse)
async def complete_habit(
    request: Request, habit_id: int, date_str: str = Form(...)
):
    user_id = get_current_user_id(request)
    toggle_habit_completed(habit_id, date_str)
    habits, days_strip = fetch_habits_with_grid(user_id)
    return templates.TemplateResponse(
        request=request,
        name="partials/habit_list.html",
        context={"habits": habits, "days_strip": days_strip},
    )


@app.delete("/habits/{habit_id}", response_class=HTMLResponse)
async def remove_habit(request: Request, habit_id: int):
    user_id = get_current_user_id(request)
    delete_habit(user_id, habit_id)
    habits, days_strip = fetch_habits_with_grid(user_id)
    return templates.TemplateResponse(
        request=request,
        name="partials/habit_list.html",
        context={"habits": habits, "days_strip": days_strip},
    )