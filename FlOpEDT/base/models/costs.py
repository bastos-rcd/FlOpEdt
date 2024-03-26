
from django.db import models


class TutorCost(models.Model):
    department = models.ForeignKey('base.Department', on_delete=models.CASCADE, null=True)
    period = models.ForeignKey('SchedulingPeriod', on_delete=models.CASCADE, null=True, blank=True)
    tutor = models.ForeignKey('people.Tutor', on_delete=models.CASCADE)
    value = models.FloatField()
    version = models.ForeignKey('base.TimetableVersion', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"sem{self.period}-{self.tutor.username}:{self.value}"


class GroupCost(models.Model):
    period = models.ForeignKey('SchedulingPeriod', on_delete=models.CASCADE, null=True, blank=True)
    group = models.ForeignKey('StructuralGroup', on_delete=models.CASCADE)
    value = models.FloatField()
    version = models.ForeignKey('base.TimetableVersion', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"sem{self.period}-{self.group}:{self.value}"


class GroupFreeHalfDay(models.Model):
    period = models.ForeignKey('SchedulingPeriod', on_delete=models.CASCADE, null=True, blank=True)
    group = models.ForeignKey('StructuralGroup', on_delete=models.CASCADE)
    DJL = models.PositiveSmallIntegerField()
    version = models.ForeignKey('base.TimetableVersion', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"sem{self.period}-{self.group}:{self.DJL}"

