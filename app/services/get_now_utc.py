from datetime import datetime, UTC


def get_now_utc():
    return datetime.now(UTC)