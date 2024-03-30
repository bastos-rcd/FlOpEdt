import datetime as dt

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from base.timing import get_default_date
from base.models.timing import Slot


class Availability(Slot):
    value = models.SmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(8)], default=8
    )
    is_default = models.BooleanField(null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.date <= dt.date(1, 1, 7):
            self.is_default = True
        self.save()

    def __str__(self):
        result = super().__str__()
        return result + f" = {self.value}"


class UserAvailability(Availability):
    user = models.ForeignKey("people.User", on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username + super().__str__()


class CourseAvailability(Availability):
    course_type = models.ForeignKey("CourseType", on_delete=models.CASCADE)
    train_prog = models.ForeignKey("TrainingProgramme", on_delete=models.CASCADE)

    def __str__(self):
        return str(self.course_type) + super().__str__()


class RoomAvailability(Availability):
    room = models.ForeignKey("Room", on_delete=models.CASCADE, default=None, null=True)

    def __str__(self):
        return str(self.room) + super().__str__()


def dated_availabilities(user, date, avail_only=False, unavail_only=False):
    if unavail_only and avail_only:
        raise ValueError("avail_only and unavail_only cannot be both True")
    user_availabilities = UserAvailability.objects.filter(user=user, date=date)
    if avail_only:
        user_availabilities = user_availabilities.filter(value__gt=0)
    if unavail_only:
        user_availabilities = user_availabilities.filter(value=0)
    return set(user_availabilities)


def default_availabilities(user, date: dt.date, avail_only=False, unavail_only=False):
    if unavail_only and avail_only:
        raise ValueError("avail_only and unavail_only cannot be both True")
    default_date = get_default_date(date)
    user_availabilities = UserAvailability.objects.filter(user=user, date=default_date)
    if avail_only:
        user_availabilities = user_availabilities.filter(value__gt=0)
    if unavail_only:
        user_availabilities = user_availabilities.filter(value=0)
    return set(user_availabilities)


def actual_availabilities(user, date: dt.date, avail_only=False, unavail_only=False):
    if dated_availabilities(user, date):
        return dated_availabilities(user, date, avail_only, unavail_only)
    result = set()
    for defaut_availability in default_availabilities(
        user, date, avail_only, unavail_only
    ):
        defaut_availability.start_time = dt.datetime.combine(
            date, defaut_availability.in_day_start_time
        )
        defaut_availability.date = date
        result.add(defaut_availability)
    return result


def period_actual_availabilities(users, periods, avail_only=False, unavail_only=False):
    result = set()
    try:
        iter(users)
    except TypeError:
        users = [users]
    try:
        iter(periods)
    except TypeError:
        periods = [periods]
    for user in users:
        for period in periods:
            for date in period.dates():
                result |= actual_availabilities(user, date, avail_only, unavail_only)
    return result
