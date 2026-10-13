from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import HTTPException


def calculate_period_bounds(
    now_utc: datetime, user_timezone: str, habit_period: str
) -> dict:

    now_local = now_utc.astimezone(ZoneInfo(user_timezone))

    if habit_period == "daily":
        start = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
    elif habit_period == "weekly":
        start = (now_local - timedelta(now_local.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end = start + timedelta(days=7)
    elif habit_period == "monthly":
        start = now_local.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        if start.month == 12:
            end = start.replace(year=start.year + 1, month=1)
        else:
            end = start.replace(month=start.month + 1)
    else:
        raise HTTPException(status_code=400, detail="Unknown period")

    return {"start": start.astimezone(UTC), "end": end.astimezone(UTC)}
