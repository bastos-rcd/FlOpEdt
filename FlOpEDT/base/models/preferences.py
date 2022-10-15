from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from base.timing import Day, str_slot, days_index, days_list

class Preference(models.Model):
    class Meta:
        abstract = True

    @property
    def end_time(self):
        return self.start_time + self.duration


class UserPreference(Preference):
    user = models.ForeignKey('people.Tutor', on_delete=models.CASCADE)
    week = models.ForeignKey('Week', on_delete=models.CASCADE, null=True, blank=True)
    day = models.CharField(
        max_length=2, choices=Day.CHOICES, default=Day.MONDAY)
    start_time = models.PositiveSmallIntegerField()  # FIXME : time with TimeField or DurationField
    duration = models.PositiveSmallIntegerField()  # FIXME : time with TimeField or DurationField
    value = models.SmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(8)],
        default=8)

    def __str__(self):
        return f"{self.user.username}-Sem{self.week}: " + \
               f"({str_slot(self.day, self.start_time, self.duration)})" + \
               f"={self.value}"

    def __lt__(self, other):
        if isinstance(other, UserPreference):
            index_day_self = days_index[self.day]
            index_day_other = days_index[other.day]
            if self.week and other.week:
                if self.week != other.week:
                    return self.week < other.week
                else:
                    if index_day_self != index_day_other:
                        return index_day_self < index_day_other
                    else:
                        return other.start_time > self.start_time + self.duration
            else:
                return index_day_self < index_day_other
        else:
            raise NotImplementedError

    def __gt__(self, other):
        if isinstance(other, UserPreference):
            index_day_self = days_index[self.day]
            index_day_other = days_index[other.day]
            if self.week and other.week:
                if self.week != other.week:
                    return self.week > other.week
                else:
                    if index_day_self != index_day_other:
                        return index_day_self > index_day_other
                    else:
                        return other.start_time > self.start_time + self.duration
            else:
                return index_day_self > index_day_other
        else:
            raise NotImplementedError

    def is_same(self, other):
        if isinstance(other, UserPreference):
            return ((((self.week and other.week) and self.week == other.week) or not self.week or not other.week)
                    and days_index[self.day] == days_index[other.day] and self.start_time == other.start_time)
        else:
            raise NotImplementedError

    def same_day(self, other):
        if isinstance(other, UserPreference):
            return days_index[self.day] == days_index[other.day]
        else:
            raise ValueError

    def is_successor_of(self, other):
        if isinstance(other, UserPreference):
            return self.same_day(other) and other.end_time <= self.start_time <= other.end_time + 30  # slot_pause
        else:
            raise ValueError


class CoursePreference(Preference):
    course_type = models.ForeignKey('CourseType', on_delete=models.CASCADE)
    train_prog = models.ForeignKey(
        'TrainingProgramme', on_delete=models.CASCADE)
    week = models.ForeignKey('Week', on_delete=models.CASCADE, null=True, blank=True)
    day = models.CharField(
        max_length=2, choices=Day.CHOICES, default=Day.MONDAY)
    start_time = models.PositiveSmallIntegerField()  # FIXME : time with TimeField or DurationField
    duration = models.PositiveSmallIntegerField()  # FIXME : time with TimeField or DurationField
    value = models.SmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(8)],
        default=8)

    def __str__(self):
        return f"{self.course_type}=Sem{self.week}:" + \
               f"({str_slot(self.day, self.start_time, self.duration)})" + \
               f"--{self.train_prog}={self.value}"


class RoomPreference(models.Model):
    room = models.ForeignKey('Room', on_delete=models.CASCADE, default=None, null=True)
    week = models.ForeignKey('Week', on_delete=models.CASCADE, null=True, blank=True)
    day = models.CharField(max_length=2, choices=Day.CHOICES, default=Day.MONDAY)
    start_time = models.PositiveSmallIntegerField()  # FIXME : time with TimeField or DurationField
    duration = models.PositiveSmallIntegerField()  # FIXME : time with TimeField or DurationField
    value = models.SmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(8)], default=8)

    def __str__(self):
        return f"{self.room}-Sem{self.week}:" + \
               f"({str_slot(self.day, self.start_time, self.duration)})" + \
               f"={self.value}"

