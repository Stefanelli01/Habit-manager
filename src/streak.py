from datetime import datetime, date, timedelta

def calculate_streak(completed_dates_str: list[str]) -> int:

    if not completed_dates_str:
        return 0

    completed_dates = [
        datetime.strptime(d, "%Y-%m-%d").date() for d in completed_dates_str
    ]

    today = date.today()
    yesterday = today - timedelta(days=1)

    latest = completed_dates[0]
    if latest not in (today, yesterday):
        return 0

    streak = 0
    expected_date = latest

    for current_date in completed_dates:
        if current_date == expected_date:
            streak += 1
            expected_date -= timedelta(days=1)

        elif current_date < expected_date:
            break

    return streak