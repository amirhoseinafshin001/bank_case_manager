import jdatetime
from datetime import datetime


def jalali_to_gregorian(jalali_date: str = None) -> datetime | None:
    if jalali_date is None:
        return None
    year, month, day = map(int, jalali_date.split("-"))
    return jdatetime.date(year, month, day).togregorian()


def gregorian_to_jalali(gregorian_date: datetime) -> str:
    shamsi_date = jdatetime.date.fromgregorian(date=gregorian_date)
    return shamsi_date.strftime("%Y-%m-%d")
