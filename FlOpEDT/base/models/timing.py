import datetime as dt

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.postgres.fields import ArrayField
from django.dispatch import receiver
from django.db.models.signals import post_save


from base.timing import Day, Time, min_to_str, days_list


class Holiday(models.Model):
    day = models.CharField(max_length=2, choices=Day.CHOICES, default=Day.MONDAY)
    week = models.ForeignKey("Week", on_delete=models.CASCADE, null=True, blank=True)

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
    day = models.CharField(max_length=2, choices=Day.CHOICES, default=Day.MONDAY)
    week = models.ForeignKey("Week", on_delete=models.CASCADE, null=True, blank=True)
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
        "base.Department", on_delete=models.CASCADE, null=True
    )
    starting_week = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)]
    )
    ending_week = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)]
    )

    class Meta:
        verbose_name = _("training period")
        verbose_name_plural = _("training periods")

    def __str__(self):
        return f"Period {self.name}: {self.department}, {self.starting_week} -> {self.ending_week}"


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

    start_date = models.DateField()
    end_date = models.DateField()
    mode = models.CharField(
        max_length=1, choices=PeriodEnum.CHOICES, default=PeriodEnum.WEEK
    )
    department = models.ForeignKey(
        "base.department", null=True, blank=True, on_delete=models.CASCADE, default=None
    )

    def __str__(self):
        ret = f"{self.start_date} - {self.end_date} ({self.mode}"
        if self.department is not None:
            ret += f", {self.department.abbrev}"
        return ret + ")"


class Week(models.Model):
    nb = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)],
        verbose_name=_("Week number"),
    )
    year = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.nb}-{self.year}"

    def __lt__(self, other):
        if isinstance(other, Week):
            return self.year < other.year or (
                self.year == other.year and self.nb < other.nb
            )
        else:
            return False

    def __gt__(self, other):
        if isinstance(other, Week):
            return self.year > other.year or (
                self.year == other.year and self.nb > other.nb
            )
        else:
            return False

    def __le__(self, other):
        return self == other or self < other

    def __ge__(self, other):
        return self == other or self > other

    class Meta:
        verbose_name = _("week")
        verbose_name_plural = _("weeks")


class TimeGeneralSettings(models.Model):
    department = models.OneToOneField("base.Department", on_delete=models.CASCADE)
    day_start_time = models.TimeField(default=dt.time(hour=8))
    morning_end_time = models.TimeField(default=dt.time(12, 30, 0))
    afternoon_start_time = models.TimeField(default=dt.time(14, 15, 0))
    day_end_time = models.TimeField(default=dt.time(hour=19))
    days = ArrayField(models.CharField(max_length=2, choices=Day.CHOICES))
    scheduling_period_mode = models.CharField(
        max_length=1, choices=PeriodEnum.CHOICES, default=PeriodEnum.WEEK
    )

    def __str__(self):
        return (
            f"Dept {self.department.abbrev}: "
            + f"{self.day_start_time} - {self.morning_end_time}"
            + f" | {self.afternoon_start_time} - "
            + f"{self.day_end_time};"
            + f" Days: {self.days}"
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

    department = models.OneToOneField("base.Department", on_delete=models.CASCADE)
    cosmo = models.PositiveSmallIntegerField(default=0, choices=cosmo_choices)
    visio = models.BooleanField(default=False)
    scheduling_mode =  models.CharField(
        max_length=1, choices=PeriodEnum.CHOICES, default=PeriodEnum.WEEK
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


@receiver(post_save, sender="base.Department")
def create_department_related(sender, instance, created, raw, **kwargs):
    if not created or raw:
        return

    Mode.objects.create(department=instance)
    TimeGeneralSettings.objects.create(
        department=instance,
        day_start_time=dt.time(6),
        day_end_time=dt.time(20),
        morning_end_time=dt.time(13),
        afternoon_start_time=dt.time(13),
        days=days_list,
    )
