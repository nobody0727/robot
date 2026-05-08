from datetime import datetime, timezone


def now_utc():
    return datetime.now(timezone.utc)


def format_datetime(dt: datetime) -> str:
    if dt:
        return dt.isoformat()
    return None


def parse_datetime(dt_str: str) -> datetime:
    if dt_str:
        return datetime.fromisoformat(dt_str)
    return None


def is_time_in_range(current: datetime.time, start: datetime.time, end: datetime.time) -> bool:
    if start <= end:
        return start <= current <= end
    else:
        return current >= start or current <= end
