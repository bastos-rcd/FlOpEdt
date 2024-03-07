from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField


class Dependency(models.Model):
    course1 = models.ForeignKey('Course', related_name='first_course', on_delete=models.CASCADE)
    course2 = models.ForeignKey('Course', related_name='second_course', on_delete=models.CASCADE)
    successive = models.BooleanField(verbose_name=_('Successives?'), default=False)
    ND = models.BooleanField(verbose_name=_('On different days'), default=False)
    day_gap = models.PositiveSmallIntegerField(verbose_name=_('Minimal day gap between courses'), default=0)

    class Meta:
        verbose_name = _("Depedency")
        verbose_name_plural = _("Dependencies")

    def __str__(self):
        return f"{self.course1} avant {self.course2}"


class Pivot(models.Model):
    pivot_course = models.ForeignKey(
        'Course', related_name='as_pivot', on_delete=models.CASCADE)
    other_courses = models.ManyToManyField('Course', related_name='as_pivot_other')
    ND = models.BooleanField(verbose_name=_('On different days'), default=False)

    def __str__(self):
        return f"{self.other_courses.all()} on the same side of {self.pivot_course}"


class CourseStartTimeConstraint(models.Model):
    # foreignkey instead of onetoone to leave room for a day attribute
    course_type = models.ForeignKey(
        'CourseType', null=True, default=None, on_delete=models.CASCADE)
    allowed_start_times = ArrayField(
        models.PositiveSmallIntegerField(), blank=True)  # FIXME : time with TimeField or DurationField


class Regen(models.Model):
    department = models.ForeignKey('base.Department', on_delete=models.CASCADE, null=True)
    week = models.ForeignKey('Week', on_delete=models.CASCADE, null=True, blank=True)
    full = models.BooleanField(verbose_name=_('Full'), default=True)
    fdate = models.DateField(verbose_name=_('Full generation date'), null=True, blank=True)
    stabilize = models.BooleanField(verbose_name=_('Stabilized'), default=False)
    sdate = models.DateField(verbose_name=_('Partial generation date'), null=True, blank=True)

    def __str__(self):
        pre = ''
        if self.full:
            pre += 'C, '
            if self.fdate is not None:
                pre += f'{self.fdate.strftime("%d/%m/%y")}, '
        if self.stabilize:
            pre += 'S, '
            if self.sdate is not None:
                pre += f'{self.sdate.strftime("%d/%m/%y")}, '
        if not self.full and not self.stabilize:
            pre = 'N, '
        pre += f"{self.id}"
        return pre

    def strplus(self):
        ret = ""
        if self.full:
            ret += f'Re-génération complète prévue le ' + \
                   f'{self.fdate.strftime("%d/%m/%y")}'
        elif self.stabilize:
            ret += 'Génération stabilisée prévue le ' + \
                   f'{self.sdate.strftime("%d/%m/%y")}'
        else:
            ret += "Pas de (re-)génération prévue"

        return ret