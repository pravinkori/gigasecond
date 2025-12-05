from datetime import timedelta

def breakdown(td: timedelta):
    total = int(td.total_seconds())
    negative = total < 0
    abs_total = abs(total)
    days = abs_total // 86400
    hours = (abs_total % 86400) // 3600
    minutes = (abs_total % 3600) // 60
    seconds = abs_total % 60
    return (days if not negative else -days), hours, minutes, seconds, total

