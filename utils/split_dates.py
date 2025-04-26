from datetime import datetime, timedelta

def split_months(year):
    """Découpe une année en mois."""
    dates = []
    for month in range(1, 13):
        start = datetime(year, month, 1)
        if month == 12:
            end = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end = datetime(year, month + 1, 1) - timedelta(days=1)
        dates.append((start.date(), end.date()))
    return dates

def split_days(year, month):
    """Découpe un mois en jours."""
    dates = []
    start = datetime(year, month, 1)
    next_month = start.replace(day=28) + timedelta(days=4)
    last_day = (next_month - timedelta(days=next_month.day)).day

    for day in range(1, last_day + 1):
        date = datetime(year, month, day).date()
        dates.append((date, date))
    return dates
