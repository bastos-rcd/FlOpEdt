import datetime as dt

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from base.timing import Day

slot_pause = 30

class Module(models.Model):
    name = models.CharField(max_length=200, null=True, verbose_name=_('name'))
    abbrev = models.CharField(max_length=100, verbose_name=_('abbreviation'))
    head = models.ForeignKey('people.Tutor', null=True, default=None, blank=True,
        on_delete=models.CASCADE, verbose_name=_('head (resp)'))
    ppn = models.CharField(max_length=30, default='M')
    train_prog = models.ForeignKey('TrainingProgramme', on_delete=models.CASCADE, verbose_name=_('training programme'))
    period = models.ForeignKey('TrainingPeriod', on_delete=models.CASCADE, verbose_name=_('training period'))
    url = models.URLField(null=True, blank=True, default=None)
    description = models.TextField(null=True, blank=True, default=None)

    def __str__(self):
        return self.abbrev

    class Meta:
        ordering = ['abbrev', ]
        verbose_name = _("module")
        verbose_name_plural = _("modules")


class ModulePossibleTutors(models.Model):
    module = models.OneToOneField('Module', on_delete=models.CASCADE)
    possible_tutors = models.ManyToManyField(
        'people.Tutor', blank=True, related_name='possible_modules')


class ModuleTutorRepartition(models.Model):
    module = models.ForeignKey('Module', on_delete=models.CASCADE)
    course_type = models.ForeignKey('CourseType', on_delete=models.CASCADE)
    tutor = models.ForeignKey('people.Tutor', on_delete=models.CASCADE)
    week = models.ForeignKey('Week', on_delete=models.CASCADE, null=True, blank=True)
    courses_nb = models.PositiveSmallIntegerField(default=1)


class CourseType(models.Model):
    name = models.CharField(max_length=50)
    department = models.ForeignKey('base.Department', on_delete=models.CASCADE, null=True)
    group_types = models.ManyToManyField('base.GroupType', blank=True, related_name="compatible_course_types")
    graded = models.BooleanField(verbose_name=_('graded?'), default=False)

    class Meta:
        verbose_name = _("course type")
        verbose_name_plural = _("course types")

    def __str__(self):
        return self.name


class Course(models.Model):
    type = models.ForeignKey('CourseType', on_delete=models.CASCADE)
    duration = models.DurationField()
    room_type = models.ForeignKey('RoomType', null=True, on_delete=models.CASCADE)
    tutor = models.ForeignKey('people.Tutor', related_name='taught_courses', null=True, blank=True,
                              default=None, on_delete=models.CASCADE)
    supp_tutor = models.ManyToManyField('people.Tutor', related_name='courses_as_supp', blank=True)
    groups = models.ManyToManyField('base.GenericGroup', related_name='courses', blank=True)
    module = models.ForeignKey('Module', related_name='courses', on_delete=models.CASCADE)
    modulesupp = models.ForeignKey('Module', related_name='courses_as_modulesupp', null=True, blank=True, on_delete=models.CASCADE)
    pay_module = models.ForeignKey('Module', related_name='courses_as_pay_module', null=True, blank=True, on_delete=models.CASCADE)
    week = models.ForeignKey('Week', on_delete=models.CASCADE, null=True, blank=True)
    suspens = models.BooleanField(verbose_name=_('Suspens?'), default=False)
    show_id = False

    class Meta:
        verbose_name = _("course")
        verbose_name_plural = _("courses")
    
    def __str__(self):
        ret = self.full_name()
        if self.show_id:
            ret += f" ({self.id})"
        return ret

    def full_name(self):
        username_mod = self.tutor.username if self.tutor is not None else '-no_tut-'
        return f"{self.type}-{self.duration}-{self.module}-{username_mod}-{'|'.join([g.name for g in self.groups.all()])}"

    def equals(self, other):
        return self.__class__ == other.__class__ \
               and self.type == other.type \
               and self.duration == other.duration \
               and self.tutor == other.tutor \
               and self.room_type == other.room_type \
               and list(self.groups.all()) == list(other.groups.all()) \
               and self.module == other.module

    def get_week(self):
        return self.week

    @property
    def is_graded(self):
        if CourseAdditional.objects.filter(course=self).exists():
            return self.additional.graded
        else:
            return self.type.graded


class CourseAdditional(models.Model):
    course = models.OneToOneField('Course', on_delete=models.CASCADE, related_name='additional')
    graded = models.BooleanField(verbose_name=_('Graded?'), default=False)
    over_time = models.BooleanField(verbose_name=_('Over time'), default=False)
    visio_preference_value = models.SmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(8)], default=1)


class CoursePossibleTutors(models.Model):
    course = models.OneToOneField('Course', on_delete=models.CASCADE)
    possible_tutors = models.ManyToManyField('people.Tutor', blank=True, related_name='shared_possible_courses')


class ScheduledCourse(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    day = models.CharField(max_length=2, choices=Day.CHOICES, default=Day.MONDAY)
    # in minutes from 12AM
    start_time = models.PositiveSmallIntegerField() # FIXME : time with TimeField or DurationField
    room = models.ForeignKey('Room', blank=True, null=True, on_delete=models.SET_NULL)
    number = models.PositiveSmallIntegerField(null=True, blank=True)
    noprec = models.BooleanField(verbose_name='vrai si on ne veut pas garder la salle', default=True)
    work_copy = models.PositiveSmallIntegerField(default=0)
    tutor = models.ForeignKey('people.Tutor', related_name='taught_scheduled_courses', 
            null=True, default=None, on_delete=models.SET_NULL)

    # les utilisateurs auront acces à la copie publique (0)

    class Meta:
        verbose_name = _("scheduled course")
        verbose_name_plural = _("scheduled courses")

    def __str__(self):
        return (f"{self.course}{self.number}:"
                f"{self.day}-t{self.start_time}-{self.room}")

    def unique_name(self):
        return (f"{self.course.type}_{self.room}_{self.tutor.username}"
                f"_{self.day}_{self.start_time}_{self.end_time}")

    @property
    def end_time(self):
        return self.start_time + self.course.type.duration

    def has_same_day(self, other):
        return self.course.week == other.course.week and self.day == other.day

    def is_successor_of(self, other):
        return self.has_same_day(other) and other.end_time <= self.start_time <= other.end_time + slot_pause

    def is_simultaneous_to(self, other):
        return self.has_same_day(other) and self.start_time < other.end_time and other.start_time < self.end_time

    @property
    def duration(self):
        return self.course.type.duration

    @property
    def pay_duration(self):
        if self.course.type.pay_duration is not None:
            return self.course.type.pay_duration
        return self.duration


class ScheduledCourseAdditional(models.Model):
    scheduled_course = models.OneToOneField('ScheduledCourse', on_delete=models.CASCADE, related_name='additional')
    link = models.ForeignKey('EnrichedLink', blank=True, null=True, default=None,
        related_name='additional', on_delete=models.SET_NULL)
    comment = models.CharField(max_length=100, null=True, default=None, blank=True)

    def __str__(self):
        resp = '{' + str(self.scheduled_course) + '}'
        if self.link.description:
            resp += '[' + str(self.link.description) + ']'
        if self.comment:
            resp += '(' + str(self.comment) + ')'
        return resp


class EnrichedLink(models.Model):
    url = models.URLField()
    description = models.CharField(max_length=100, null=True, default=None, blank=True)

    @property
    def concatenated(self):
        return ' '.join(
            [str(self.id),
             self.url,
             self.description if self.description is not None else '']
        )

    def __str__(self):
        return (self.description if self.description is not None else '') \
               + ' -> ' + self.url


class GroupPreferredLinks(models.Model):
    group = models.OneToOneField('base.StructuralGroup', on_delete=models.CASCADE, related_name='preferred_links')
    links = models.ManyToManyField('EnrichedLink', related_name='group_set')

    def __str__(self):
        return self.group.full_name + ' : ' + \
               ' ; '.join([str(l) for l in self.links.all()])
