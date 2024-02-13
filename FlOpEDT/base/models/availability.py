from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from base.timing import Day, str_slot, days_index, days_list

from datetime import date, time, timedelta, datetime


class Availability(models.Model):
    in_day_start_time = models.TimeField(default=time(0))
    date = models.DateField(default=date(1, 1, 1))
    duration = models.DurationField(default=timedelta(0))

    value = models.SmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(8)], default=8
    )

    class Meta:
        abstract = True

    @property
    def start_time(self):
        return datetime.combine(self.date, self.in_day_start_time)

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


class UserAvailability(Availability):
    user = models.ForeignKey("people.User", on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username + super().__str__()

    # def is_same(self, other):
    #     if isinstance(other, UserAvailability):
    #         return (
    #             (
    #                 ((self.week and other.week) and self.week == other.week)
    #                 or not self.week
    #                 or not other.week
    #             )
    #             and days_index[self.day] == days_index[other.day]
    #             and self.start_time == other.start_time
    #         )
    #     else:
    #         raise NotImplementedError

    # def same_day(self, other):
    #     if isinstance(other, UserAvailability):
    #         return days_index[self.day] == days_index[other.day]
    #     else:
    #         raise ValueError

    # def is_successor_of(self, other):
    #     if isinstance(other, UserAvailability):
    #         return (
    #             self.same_day(other)
    #             and other.end_time <= self.start_time <= other.end_time + 30
    #         )  # slot_pause
    #     else:
    #         raise ValueError


class CourseAvailability(Availability):
    course_type = models.ForeignKey("CourseType", on_delete=models.CASCADE)
    train_prog = models.ForeignKey("TrainingProgramme", on_delete=models.CASCADE)

    def __str__(self):
        return str(self.course_type) + super().__str__()


class RoomAvailability(Availability):
    room = models.ForeignKey("Room", on_delete=models.CASCADE, default=None, null=True)

    def __str__(self):
        return str(self.room) + super().__str__()
