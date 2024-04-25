import datetime as dt

from django.apps import apps
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from base.timing import Day, Time, days_list, slot_pause


class Holiday(models.Model):
    date = models.DateField(default=dt.date(1890, 5, 1))

    class Meta:
        verbose_name = _("holiday")
        verbose_name_plural = _("holidays")


class TrainingHalfDay(models.Model):
    apm = models.CharField(
        max_length=2,
        choices=Time.HALF_DAY_CHOICES,
        verbose_name=_("Half day"),
        null=True,
        default=None,
        blank=True,
    )
    date = models.DateField(default=dt.date(1890, 5, 1))
    train_prog = models.ForeignKey(
        "TrainingProgramme",
        null=True,
        default=None,
        blank=True,
        on_delete=models.CASCADE,
    )


class TrainingPeriod(models.Model):
    name = models.CharField(max_length=20)
    department = models.ForeignKey(
        "base.Department",
        on_delete=models.CASCADE,
        null=True,
        related_name="training_periods",
    )
    periods = models.ManyToManyField("SchedulingPeriod")

    class Meta:
        verbose_name = _("training period")
        verbose_name_plural = _("training periods")

    def __str__(self):
        result = f"Period {self.name}: {self.department}"
        if self.periods.exists():
            result += (
                f", {min(sp.start_date for sp in self.periods.all())}"
                f"-> {max(sp.end_date for sp in self.periods.all())}"
            )
        else:
            result += ", no period"
        return result


class PeriodEnum:
    DAY = "d"
    WEEK = "w"
    MONTH = "m"
    YEAR = "y"
    CUSTOM = "c"

    CHOICES = [
        (DAY, _("day")),
        (WEEK, _("week")),
        (MONTH, _("month")),
        (YEAR, _("year")),
        (CUSTOM, _("custom")),
    ]


class SchedulingPeriod(models.Model):
    """
    start_date and end_date included
    """

    name = models.CharField(max_length=20, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    mode = models.CharField(
        max_length=1, choices=PeriodEnum.CHOICES, default=PeriodEnum.WEEK
    )
    department = models.ForeignKey(
        "base.department", null=True, blank=True, on_delete=models.CASCADE, default=None
    )

    def __str__(self):
        return self.name

    def __lte__(self, other):
        if isinstance(other, SchedulingPeriod):
            return self.start_date <= other.start_date
        if isinstance(other, dt.date):
            return self.start_date <= other
        raise TypeError(f"Cannot compare {type(self)} with {type(other)}")

    def __lt__(self, other):
        if isinstance(other, SchedulingPeriod):
            return self.end_date < other.start_date
        if isinstance(other, dt.date):
            return self.end_date < other
        raise TypeError(f"Cannot compare {type(self)} with {type(other)}")

    def __gt__(self, other):
        if isinstance(other, SchedulingPeriod):
            return self.start_date > other.end_date
        if isinstance(other, dt.date):
            return self.start_date > other
        raise TypeError(f"Cannot compare {type(self)} with {type(other)}")

    def __gte__(self, other):
        if isinstance(other, SchedulingPeriod):
            return self.end_date >= other.end_date
        if isinstance(other, dt.date):
            return self.end_date >= other
        raise TypeError(f"Cannot compare {type(self)} with {type(other)}")

    def dates(self):
        return [
            self.start_date + dt.timedelta(days=i)
            for i in range((self.end_date - self.start_date).days + 1)
        ]

    def index(self, date):
        return self.dates().index(date)

    def related_departments(self):
        if self.department:
            return [self.department]
        department_model = apps.get_model("base.Department")
        return list(department_model.objects.filter(mode__scheduling_mode=self.mode))


class TimeGeneralSettings(models.Model):
    department = models.OneToOneField("base.Department", on_delete=models.CASCADE)
    day_start_time = models.TimeField(default=dt.time(hour=8))
    morning_end_time = models.TimeField(default=dt.time(12, 30, 0))
    afternoon_start_time = models.TimeField(default=dt.time(14, 15, 0))
    day_end_time = models.TimeField(default=dt.time(hour=19))
    weekdays = ArrayField(models.CharField(max_length=2, choices=Day.CHOICES))
    scheduling_period_mode = models.CharField(
        max_length=1, choices=PeriodEnum.CHOICES, default=PeriodEnum.WEEK
    )

    @property
    def days(self):
        return self.weekdays

    def __str__(self):
        return (
            f"Dept {self.department.abbrev}: "
            + f"{self.day_start_time} - {self.morning_end_time}"
            + f" | {self.afternoon_start_time} - "
            + f"{self.day_end_time};"
            + f" Days: {self.weekdays}"
        )


class Mode(models.Model):
    """
    cosmo has to be:
     - 0 for educational mode
     - 1 for employee cooperatives in which columns are workplaces
     - 2 for employee cooperatives in which columns are employees
    """

    EDUCATIVE = 0
    COOPERATIVE_BY_WORKPLACE = 1
    COOPERATIVE_BY_WORKER = 2

    cosmo_choices = (
        (EDUCATIVE, _("Educative")),
        (COOPERATIVE_BY_WORKPLACE, _("Coop. (workplace)")),
        (COOPERATIVE_BY_WORKER, _("Coop. (worker)")),
    )
    scheduling_mode_choices = PeriodEnum.CHOICES

    department = models.OneToOneField("base.Department", on_delete=models.CASCADE)
    cosmo = models.PositiveSmallIntegerField(default=0, choices=cosmo_choices)
    visio = models.BooleanField(default=False)
    scheduling_mode = models.CharField(
        max_length=1, choices=scheduling_mode_choices, default=PeriodEnum.WEEK
    )

    def __str__(self):
        text = f"Dept {self.department.abbrev}: "
        if not self.cosmo:
            text += "educational mode "
        else:
            text += f"cosmo {self.cosmo} mode "
        if self.visio:
            text += "with "
        else:
            text += "without "
        text += "visio."
        return text


class Slot(models.Model):
    start_time = models.DateTimeField(default=dt.datetime(1871, 3, 18))
    date = models.DateField(default=dt.date(1, 1, 1))

    def save(self, *args, **kwargs):
        force_date = kwargs.pop("force_date") if "force_date" in kwargs else False
        if force_date is False:
            self.date = self.start_time.date()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True

    def is_simultaneous_to(self, other: "Slot"):
        return self.start_time < other.end_time and self.end_time > other.start_time

    def __lt__(self, other):
        if isinstance(other, Slot):
            return self.end_time < other.start_time
        raise NotImplementedError

    def __gt__(self, other):
        if isinstance(other, Slot):
            return self.start_time > other.end_time
        raise NotImplementedError

    def has_same_date(self, other: "Slot"):
        return self.date == other.date

    def is_successor_of(self, other: "Slot"):
        return other.end_time <= self.start_time <= other.end_time + slot_pause

    def weekday_is(self, weekday):
        return days_list[self.date.weekday()] == weekday

    def weekday__in(self, weekdays):
        return days_list[self.date.weekday()] in weekdays

    @property
    def duration(self):
        raise NotImplementedError

    @property
    def in_day_start_time(self):
        return self.start_time.time()

    @property
    def end_time(self):
        return self.start_time + self.duration

    @property
    def in_day_end_time(self):
        return self.end_time.time()

    @property
    def minutes(self):
        return self.duration.total_seconds() // 60

    @property
    def start_date(self):
        return self.date

    @property
    def weekday(self):
        return days_list[self.date.weekday()]

    @property
    def apm(self):
        return Time.get_apm(self.start_time)

    @property
    def week_number(self):
        return self.date.isocalendar()[1]

    def __str__(self):
        return (
            f"{self.date:%d/%m/%y}: "
            + f"{self.in_day_start_time:%H:%M}-{self.in_day_end_time:%H:%M}"
        )


@receiver(post_save, sender="base.Department")
def create_department_related(
    sender, instance, created, raw, **kwargs
):  # pylint: disable=unused-argument
    if not created or raw:
        return
    mode_model = apps.get_model("base.Mode")
    time_general_settings_model = apps.get_model("base.TimeGeneralSettings")
    mode_model.objects.create(department=instance)
    time_general_settings_model.objects.create(
        department=instance,
        day_start_time=dt.time(6),
        day_end_time=dt.time(20),
        morning_end_time=dt.time(13),
        afternoon_start_time=dt.time(13),
        weekdays=days_list,
    )
