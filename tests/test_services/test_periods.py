from datetime import datetime, UTC

import pytest
from fastapi import HTTPException

from app.services.calculate_period_bounds import calculate_period_bounds


def test_periods_daily_period_bounds():
    now_utc = datetime(2026, 10, 11, 12, 30, tzinfo=UTC)

    result = calculate_period_bounds(
        now_utc=now_utc,
        user_timezone="Europe/Moscow",
        habit_period="daily"
    )

    assert result["start"] == datetime(2026, 10, 10, 21, 0, tzinfo=UTC)
    assert result["end"] == datetime(2026, 10, 11, 21, 0, tzinfo=UTC)


def test_periods_weekly_period_bounds():
    now_utc = datetime(2026, 10, 11, 12, 30, tzinfo=UTC)

    result = calculate_period_bounds(
        now_utc=now_utc,
        user_timezone="Europe/Moscow",
        habit_period="weekly"
    )

    assert result["start"] == datetime(2026, 10, 4, 21, 0, tzinfo=UTC)
    assert result["end"] == datetime(2026, 10, 11, 21, 0, tzinfo=UTC)


def test_periods_monthly_period_bounds():
    now_utc = datetime(2026, 10, 11, 12, 30, tzinfo=UTC)

    result = calculate_period_bounds(
        now_utc=now_utc,
        user_timezone="Europe/Moscow",
        habit_period="monthly"
    )

    assert result["start"] == datetime(2026, 9, 30, 21, 0, tzinfo=UTC)
    assert result["end"] == datetime(2026, 10, 31, 21, 0, tzinfo=UTC)


def test_periods_monthly_from_december_to_january():
    now_utc = datetime(2027, 1, 11, 12, 30, tzinfo=UTC)

    result = calculate_period_bounds(
        now_utc=now_utc,
        user_timezone="Europe/Moscow",
        habit_period="monthly"
    )

    assert result["start"] == datetime(2026, 12, 31, 21, 0, tzinfo=UTC)
    assert result["end"] == datetime(2027, 1, 31, 21, 0, tzinfo=UTC)


def test_periods_monthly_february_bounds():
    now_utc = datetime(2027, 2, 7, 12, 30, tzinfo=UTC)

    result = calculate_period_bounds(
        now_utc=now_utc,
        user_timezone="Europe/Moscow",
        habit_period="monthly"
    )

    assert result["start"] == datetime(2027, 1, 31, 21, 0, tzinfo=UTC)
    assert result["end"] == datetime(2027, 2, 28, 21, 0, tzinfo=UTC)


def test_periods_unknown_period():
    now_utc = datetime(2027, 2, 7, 12, 30, tzinfo=UTC)

    with pytest.raises(HTTPException) as exc_info:
        result = calculate_period_bounds(
            now_utc=now_utc,
            user_timezone="Europe/Moscow",
            habit_period="unknown-period"
        )

        exc_info["status_code"] == 400
        exc_info["detail"] == "Unknown period"