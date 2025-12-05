from datetime import datetime, timedelta

BILLION = 1_000_000_000
FORMATS = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"]

def parse_dob(dob_str: str) -> datetime:
    dob_str = dob_str.strip()
    for fmt in FORMATS:
        try:
            dt = datetime.strptime(dob_str, fmt)
            if fmt == "%Y-%m-%d":
                return datetime(dt.year, dt.month, dt.day, 0, 0, 0)
            return dt
        except ValueError:
            continue
    raise ValueError("Invalid date format. Use YYYY-MM-DD or YYYY-MM-DD HH:MM")

def age_seconds(dob: datetime, now: datetime | None = None) -> int:
    now = now or datetime.now()
    return int((now - dob).total_seconds())

def milestone_datetime(dob: datetime, seconds: int) -> datetime:
    return dob + timedelta(seconds=seconds)

def time_until_milestone(dob: datetime, seconds: int, now: datetime | None = None) -> timedelta:
    now = now or datetime.now()
    return milestone_datetime(dob, seconds) - now
