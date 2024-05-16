import datetime as dt
from calendar import isleap, monthrange

from base.models.timing import PeriodEnum


def generate_scheduling_periods(
    from_date: dt.datetime, to_date: dt.datetime, scheduling_period_model
):
    objects = []

    current = from_date
    while current <= to_date:
        objects.append(
            scheduling_period_model(
                start_date=current,
                end_date=current,
                mode=PeriodEnum.DAY,
                name=str(current),
            )
        )
        current += dt.timedelta(days=1)

    current = from_date - dt.timedelta(days=from_date.isocalendar().weekday - 1)
    while current <= to_date:
        objects.append(
            scheduling_period_model(
                start_date=current,
                end_date=current + dt.timedelta(days=6),
                mode=PeriodEnum.WEEK,
                name=f"W{current.isocalendar().week}-{current.isocalendar().year}",
            )
        )
        current += dt.timedelta(days=7)

    current = dt.date(year=from_date.year, month=from_date.month, day=1)
    while current <= to_date:
        future = current + dt.timedelta(days=monthrange(current.year, current.month)[1])
        objects.append(
            scheduling_period_model(
                start_date=current,
                end_date=future - dt.timedelta(days=1),
                mode=PeriodEnum.MONTH,
                name=current.strftime("%B_%Y"),
            )
        )
        current = future

    current = dt.date(year=from_date.year, month=1, day=1)
    while current <= to_date:
        ndays = 366 if isleap(current.year) else 365
        future = current + dt.timedelta(days=ndays)
        objects.append(
            scheduling_period_model(
                start_date=current,
                end_date=future - dt.timedelta(days=1),
                mode=PeriodEnum.YEAR,
                name=str(current.year),
            )
        )
        current = future

    scheduling_period_model.objects.bulk_create(objects)