from datetime import timedelta

def breakdown(td: timedelta) -> tuple[int, int, int, int, int]:
    total = int(td.total_seconds())
    if total < 0:
        total = abs(total)
        negative = True
    else:
        negative = False
    days = total // 86400
    hours = (total % 86400) // 3600
    minutes = (total % 3600) // 60
    seconds = total % 60
    if negative:
        return -days, hours, minutes, seconds, int(td.total_seconds())
    return days, hours, minutes, seconds, int(td.total_seconds())
