from datetime import UTC, datetime


def get_now_utc():
    return datetime.now(UTC)
