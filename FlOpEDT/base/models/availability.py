from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from base.timing import Day, str_slot, days_index, days_list

import datetime as dt 

class Availability(models.Model):
    start_time = models.DateTimeField(default=dt.datetime(1871, 3, 18))
    date = models.DateField(default=dt.date(1, 1, 1))
    duration = models.DurationField(default=dt.timedelta(0))
    value = models.SmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(8)], default=8
    )
    is_default = models.BooleanField(null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        force_date = kwargs.pop("force_date") if "force_date" in kwargs else False
        if force_date is False:
            self.date = self.start_time.date()
        if self.date <= dt.date(1,1,7):
            self.is_default = True
        super(Availability, self).save(*args, **kwargs)

    @property
    def in_day_start_time(self):
        return self.start_time.time()

    @property
    def end_time(self):
        return self.start_time + self.duration

    @property
    def in_day_end_time(self):
        return self.end_time.time()

    def __str__(self):
        return (
            f" - {self.date:%d/%m/%y}: "
            + f"({self.in_day_start_time:%H:%M}-{self.in_day_end_time:%H:%M})"
            + f" = {self.value}"
        )

    def __lt__(self, other):
        if isinstance(other, Availability):
            return self.end_time < other.start_time
        else:
            raise NotImplementedError

    def __gt__(self, other):
        if isinstance(other, Availability):
            return self.start_time > other.end_time
        else:
            raise NotImplementedError
    
    def weekday_is(self, week_day):
        return days_list[self.date.weekday()] == week_day
    
    def weekday__in(self, week_days):
        return days_list[self.date.weekday()] in week_days
    


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
