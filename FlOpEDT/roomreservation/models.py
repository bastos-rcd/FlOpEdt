from colorfield.fields import ColorField
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

from base.timing import Day


class RoomReservation(models.Model):
    responsible = models.ForeignKey('people.User', on_delete=models.CASCADE, related_name='reservationResp')
    room = models.ForeignKey('base.Room', on_delete=models.CASCADE, related_name='reservationRoom')
    reservation_type = models.ForeignKey('RoomReservationType', on_delete=models.SET_NULL, blank=True, null=True)
    title = models.CharField(max_length=30)
    description = models.TextField(null=True, blank=True)
    email = models.BooleanField(default=False)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    periodicity = models.ForeignKey("ReservationPeriodicity", null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.room}-{self.date}  {self.start_time}/{self.end_time}"

    def unique_name(self):
        return f"{self.date}_{self.reservation_type.name}_{self.room}_{self.responsible.username}_{self.start_time}_{self.end_time}"

    @property
    def duration(self):
        return (self.end_time.hour - self.start_time.hour)*60 + (self.end_time.minute - self.start_time.minute)


class RoomReservationType(models.Model):
    name = models.CharField(max_length=30)
    bg_color = ColorField(default='#95a5a6')

    def __str__(self):
        return self.name


class ReservationPeriodicity(models.Model):
    start = models.DateField(blank=True)
    end = models.DateField(blank=True)

    class PeriodicityType(models.TextChoices):
        # EachDay = 'ED', _('Each day')
        ByWeek = 'BW', _('By week')
        EachMonthSameDate = 'EM', _('Each month at the same date')
        ByMonth = 'BM', _('By Month')

    periodicity_type = models.CharField(
        max_length=2,
        choices=PeriodicityType.choices,
        default=PeriodicityType.ByWeek,
    )


class ReservationPeriodicityByWeek(ReservationPeriodicity):
    """
    This reservation will be replicated each n week (with n = bw_weeks_interval)
    """
    periodicity = models.OneToOneField(ReservationPeriodicity, parent_link=True, on_delete=models.CASCADE,
                                       related_name='BW')

    # Weekdays which must be included in the reservation
    bw_weekdays = ArrayField(models.CharField(max_length=2,
                                              choices=Day.CHOICES))
    bw_weeks_interval = models.PositiveSmallIntegerField(default=1)

    def save(self, **kwargs):
        self.periodicity_type = 'BW'
        super(ReservationPeriodicity, self).save(**kwargs)


class ReservationPeriodicityEachMonthSameDate(ReservationPeriodicity):
    periodicity = models.OneToOneField(ReservationPeriodicity, parent_link=True, on_delete=models.CASCADE,
                                       related_name='EM')
    def save(self, **kwargs):
        self.periodicity_type = 'EM'
        super(ReservationPeriodicity, self).save(**kwargs)


class ReservationPeriodicityByMonth(ReservationPeriodicity):
    """
    This reservation will be replicated each Xth Y of the month (with Y = bm_day_choice)
    """
    periodicity = models.OneToOneField(ReservationPeriodicity, parent_link=True, on_delete=models.CASCADE,
                                       related_name='BM')

    class ByMonthX(models.IntegerChoices):
        First = 1, _('First')
        Second = 2, _('Second')
        Third = 3, _('Third')
        Fourth = 4, _('Fourth')
        AnteLast = -2, _('Ante Last')
        Last = -1, _('Last')

    bm_x_choice = models.SmallIntegerField(choices=ByMonthX.choices)
    bm_day_choice = models.CharField(max_length=2, choices=Day.CHOICES)

    def save(self, **kwargs):
        self.periodicity_type = 'BM'
        super(ReservationPeriodicity, self).save(**kwargs)
