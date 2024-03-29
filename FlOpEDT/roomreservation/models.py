from colorfield.fields import ColorField
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

from base.timing import Day


class RoomReservation(models.Model):
    responsible = models.ForeignKey(
        "people.User", on_delete=models.CASCADE, related_name="reservationResp"
    )
    room = models.ForeignKey(
        "base.Room", on_delete=models.CASCADE, related_name="reservationRoom"
    )
    reservation_type = models.ForeignKey(
        "RoomReservationType", on_delete=models.SET_NULL, blank=True, null=True
    )
    title = models.CharField(max_length=30)
    description = models.TextField(null=True, blank=True)
    email = models.BooleanField(default=False)
    date = models.DateField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    periodicity = models.ForeignKey(
        "ReservationPeriodicity", null=True, blank=True, on_delete=models.SET_NULL
    )

    def save(self, *args, **kwargs):
        force_date = kwargs.pop("force_date") if "force_date" in kwargs else False
        if force_date is False:
            self.date = self.start_time.date()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.room}-{self.date}  {self.start_time}/{self.end_time}"

    def unique_name(self):
        type_name = self.reservation_type.name if self.reservation_type else "noType"
        return (
            f"{self.date}_{type_name}_{self.room}_{self.responsible.username}"
            "_{self.start_time}_{self.end_time}"
        )

    @property
    def duration(self):
        return self.end_time - self.start_time

    @property
    def minutes(self):
        return self.duration.seconds // 60

    @property
    def start_date(self):
        return self.date

    @property
    def end_date(self):
        return self.end_time.date()


class RoomReservationType(models.Model):
    name = models.CharField(max_length=30)
    bg_color = ColorField(default="#95a5a6")

    def __str__(self):
        return self.name


class ReservationPeriodicity(models.Model):
    start = models.DateField(blank=True)
    end = models.DateField(blank=True)

    class PeriodicityType(models.TextChoices):
        # EachDay = 'ED', _('Each day')
        BY_WEEK = "BW", _("By week")
        EACH_MONTH_SAME_DATE = "EM", _("Each month at the same date")
        BY_MONTH = "BM", _("By Month")

    periodicity_type = models.CharField(
        max_length=2,
        choices=PeriodicityType.choices,
        default=PeriodicityType.BY_WEEK,
    )


class ReservationPeriodicityByWeek(ReservationPeriodicity):
    """
    This reservation will be replicated each n week (with n = bw_weeks_interval)
    """

    periodicity = models.OneToOneField(
        ReservationPeriodicity,
        parent_link=True,
        on_delete=models.CASCADE,
        related_name=ReservationPeriodicity.PeriodicityType.BY_WEEK,
    )

    # Weekdays which must be included in the reservation
    bw_weekdays = ArrayField(models.CharField(max_length=2, choices=Day.CHOICES))
    bw_weeks_interval = models.PositiveSmallIntegerField(default=1)

    def save(self, *args, **kwargs):
        self.periodicity_type = ReservationPeriodicity.PeriodicityType.BY_WEEK
        super(ReservationPeriodicity, self).save(*args, **kwargs)


class ReservationPeriodicityEachMonthSameDate(ReservationPeriodicity):
    periodicity = models.OneToOneField(
        ReservationPeriodicity,
        parent_link=True,
        on_delete=models.CASCADE,
        related_name=ReservationPeriodicity.PeriodicityType.EACH_MONTH_SAME_DATE,
    )

    def save(self, *args, **kwargs):
        self.periodicity_type = (
            ReservationPeriodicity.PeriodicityType.EACH_MONTH_SAME_DATE
        )
        super(ReservationPeriodicity, self).save(*args, **kwargs)


class ReservationPeriodicityByMonth(ReservationPeriodicity):
    """
    This reservation will be replicated each Xth Y of the month (with Y = bm_day_choice)
    """

    periodicity = models.OneToOneField(
        ReservationPeriodicity,
        parent_link=True,
        on_delete=models.CASCADE,
        related_name=ReservationPeriodicity.PeriodicityType.BY_MONTH,
    )

    class ByMonthX(models.IntegerChoices):
        FIRST = 1, _("First")
        SECOND = 2, _("Second")
        THIRD = 3, _("Third")
        FOURTH = 4, _("Fourth")
        PENULTIMATE = -2, _("Penultimate")
        LAST = -1, _("Last")

    bm_x_choice = models.SmallIntegerField(choices=ByMonthX.choices)
    bm_day_choice = models.CharField(max_length=2, choices=Day.CHOICES)

    def save(self, *args, **kwargs):
        self.periodicity_type = ReservationPeriodicity.PeriodicityType.BY_MONTH
        super(ReservationPeriodicity, self).save(*args, **kwargs)


class RoomReservationValidationEmail(models.Model):
    room = models.OneToOneField("base.Room", models.CASCADE)
    validators = models.ManyToManyField("people.User")
