from datetime import timezone, timedelta, datetime
from dateutil.relativedelta import relativedelta


def timestamp_to_iso(timestamp):
    JST = timezone(timedelta(hours=+9), 'JST')
    iso = datetime.fromtimestamp(timestamp, JST).isoformat()
    return iso


def get_today():
    JST = timezone(timedelta(hours=+9), 'JST')
    dt = datetime.now(JST)
    # d = dt.date()
    return dt


def jst_now():
    JST = timezone(timedelta(hours=+9), 'JST')
    return datetime.now(JST)


def jst_now_str(format="%Y-%m-%d"):
    JST = timezone(timedelta(hours=+9), 'JST')
    return datetime.now(JST).strftime(format)


def iso_to_timestamp(iso):
    return datetime.fromisoformat(iso).timestamp()


def get_first_day(dt):
    return dt.replace(day=1)


def relative_date(d, years: int = 0, months: int = 0, days: int = 0):
    relative_date = d + relativedelta(years=years, months=months, days=days)
    return relative_date
