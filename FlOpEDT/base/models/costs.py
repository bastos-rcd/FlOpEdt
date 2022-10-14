
from django.db import models

class TutorCost(models.Model):
    department = models.ForeignKey('base.Department', on_delete=models.CASCADE, null=True)
    week = models.ForeignKey('Week', on_delete=models.CASCADE, null=True, blank=True)
    tutor = models.ForeignKey('people.Tutor', on_delete=models.CASCADE)
    value = models.FloatField()
    work_copy = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"sem{self.week}-{self.tutor.username}:{self.value}"


class GroupCost(models.Model):
    week = models.ForeignKey('Week', on_delete=models.CASCADE, null=True, blank=True)
    group = models.ForeignKey('StructuralGroup', on_delete=models.CASCADE)
    value = models.FloatField()
    work_copy = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"sem{self.week}-{self.group}:{self.value}"


class GroupFreeHalfDay(models.Model):
    week = models.ForeignKey('Week', on_delete=models.CASCADE, null=True, blank=True)
    group = models.ForeignKey('StructuralGroup', on_delete=models.CASCADE)
    DJL = models.PositiveSmallIntegerField()
    work_copy = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"sem{self.week}-{self.group}:{self.DJL}"

