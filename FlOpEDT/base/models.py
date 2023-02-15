# coding: utf-8
# -*- coding: utf-8 -*-

# This file is part of the FlOpEDT/FlOpScheduler project.
# Copyright (c) 2017
# Authors: Iulian Ober, Paul Renaud-Goud, Pablo Seban, et al.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with this program. If not, see
# <http://www.gnu.org/licenses/>.
#
# You can be released from the requirements of the license by purchasing
# a commercial license. Buying such a license is mandatory as soon as
# you develop activities involving the FlOpEDT/FlOpScheduler software
# without disclosing the source code of your own applications.

from enum import Enum

from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

import base.weeks
from base.timing import hhmm, str_slot, Day, Time, days_list, days_index

slot_pause = 30


###
#
# Theme
# Allows to define a theme for a user,
# The value will be the one showed in the user preferrences (in the menu)
# It will also be used by the "base.html" file in the "if" conditions
#
###
class Theme(Enum):
    WHITE = 'White'
    DARK = 'Dark'
    SYNTH_WAVE = 'SynthWave'
    BRUME = 'Brume'
    PRESTIGE = 'Prestige Edition'
    PINK = 'Pink'


# <editor-fold desc="GROUPS">
# ------------
# -- GROUPS --
# ------------

class Department(models.Model):
    name = models.CharField(max_length=50)
    abbrev = models.CharField(max_length=7)

    def __str__(self):
        return self.abbrev


class TrainingProgramme(models.Model):
    name = models.CharField(max_length=50)
    abbrev = models.CharField(max_length=50)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.abbrev


class GroupType(models.Model):
    name = models.CharField(max_length=50)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name


class GenericGroup(models.Model):
    # should not include "-" nor "|"
    name = models.CharField(max_length=100)
    train_prog = models.ForeignKey(
        'TrainingProgramme', on_delete=models.CASCADE)
    type = models.ForeignKey('GroupType', on_delete=models.CASCADE, null=True)
    size = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = (("name", "train_prog"),)

    @property
    def full_name(self):
        return self.train_prog.abbrev + "-" + self.name

    def __str__(self):
        return self.full_name

    def ancestor_groups(self):
        if self.is_structural:
            return self.structuralgroup.ancestor_groups()
        return set()

    def descendants_groups(self):
        if self.is_structural:
            return self.structuralgroup.descendants_groups()
        return set()

    @property
    def is_structural(self):
        try:
            self.structuralgroup
            return True
        except:
            return False

    @property
    def is_transversal(self):
        try:
            self.transversalgroup
            return True
        except:
            return False


class StructuralGroup(GenericGroup):
    basic = models.BooleanField(verbose_name=_('Basic group?'), default=False)
    parent_groups = models.ManyToManyField('self', symmetrical=False,
                                           blank=True,
                                           related_name="children_groups")
    generic = models.OneToOneField('GenericGroup', on_delete=models.CASCADE, parent_link=True)

    def ancestor_groups(self):
        """
        :return: the set of all StructuralGroup containing self (self not included)
        """
        ancestors = set(self.parent_groups.all())

        for gp in self.parent_groups.all():

            for new_gp in gp.ancestor_groups():
                ancestors.add(new_gp)

        return ancestors

    def and_ancestors(self):
        """
        :return: the set of all StructuralGroup containing self (self included)
        """
        return {self} | self.ancestor_groups()

    def descendants_groups(self):
        """
        :return: the set of all StructuralGroup contained by self (self not included)
        """
        descendants = set()

        for gp in StructuralGroup.objects.filter(train_prog=self.train_prog):
            if self in gp.ancestor_groups():
                descendants.add(gp)

        return descendants

    def basic_groups(self):
        s = set(g for g in self.descendants_groups() | {self} if g.basic)
        return s

    def connected_groups(self):
        """
        :return: the set of all StructuralGroup that have a non empty intersection with self (self included)
        """
        return {self} | self.descendants_groups() | self.ancestor_groups()

    @property
    def transversal_conflicting_groups(self):
        """
        :return: the set of all TransversalGroup containing self
        """
        return TransversalGroup.objects.filter(conflicting_groups__in=self.connected_groups())


class TransversalGroup(GenericGroup):
    conflicting_groups = models.ManyToManyField("base.StructuralGroup", blank=True)

    parallel_groups = models.ManyToManyField('self', symmetrical=True,
                                             blank=True)
    generic = models.OneToOneField('GenericGroup', on_delete=models.CASCADE, parent_link=True)

    def nb_of_courses(self, week):
        return len(Course.objects.filter(week=week, groups=self))

    def time_of_courses(self, week):
        t = 0
        for c in Course.objects.filter(week=week, groups=self):
            t += c.type.duration
        return t


# </editor-fold desc="GROUPS">


# <editor-fold desc="TIMING">
# ------------
# -- TIMING --
# ------------


class Holiday(models.Model):
    day = models.CharField(
        max_length=2, choices=Day.CHOICES, default=Day.MONDAY)
    week = models.ForeignKey('Week', on_delete=models.CASCADE, null=True, blank=True)


class TrainingHalfDay(models.Model):
    apm = models.CharField(max_length=2, choices=Time.HALF_DAY_CHOICES,
                           verbose_name=_("Half day"), null=True, default=None, blank=True)
    day = models.CharField(
        max_length=2, choices=Day.CHOICES, default=Day.MONDAY)
    week = models.ForeignKey('Week', on_delete=models.CASCADE, null=True, blank=True)
    train_prog = models.ForeignKey(
        'TrainingProgramme', null=True, default=None, blank=True, on_delete=models.CASCADE)


class Period(models.Model):
    name = models.CharField(max_length=20)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, null=True)
    starting_week = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)])
    ending_week = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)])

    def __str__(self):
        return f"Period {self.name}: {self.department}, {self.starting_week} -> {self.ending_week}"


class Week(models.Model):
    nb = models.PositiveSmallIntegerField(validators=[MinValueValidator(0),
                                                      MaxValueValidator(53)],
                                          verbose_name=_('Week number'))
    year = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.nb}-{self.year}"

    def __lt__(self, other):
        if isinstance(other, Week):
            return self.year < other.year or (self.year == other.year and self.nb < other.nb)
        else:
            return False

    def __gt__(self, other):
        if isinstance(other, Week):
            return self.year > other.year or (self.year == other.year and self.nb > other.nb)
        else:
            return False

    def __le__(self, other):
        return self == other or self < other

    def __ge__(self, other):
        return self == other or self > other


class TimeGeneralSettings(models.Model):
    department = models.OneToOneField(Department, on_delete=models.CASCADE)
    day_start_time = models.PositiveSmallIntegerField()
    day_finish_time = models.PositiveSmallIntegerField()
    lunch_break_start_time = models.PositiveSmallIntegerField()
    lunch_break_finish_time = models.PositiveSmallIntegerField()
    days = ArrayField(models.CharField(max_length=2,
                                       choices=Day.CHOICES))
    default_preference_duration = models.PositiveSmallIntegerField(default=90)

    def __str__(self):
        return f"Dept {self.department.abbrev}: " + \
               f"{hhmm(self.day_start_time)} - {hhmm(self.lunch_break_start_time)}" + \
               f" | {hhmm(self.lunch_break_finish_time)} - " + \
               f"{hhmm(self.day_finish_time)};" + \
               f" Days: {self.days}"


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

    cosmo_choices = ((EDUCATIVE, _("Educative")),
                     (COOPERATIVE_BY_WORKPLACE, _("Coop. (workplace)")),
                     (COOPERATIVE_BY_WORKER, _("Coop. (worker)")))

    department = models.OneToOneField(Department,
                                      on_delete=models.CASCADE)
    cosmo = models.PositiveSmallIntegerField(default=0, choices=cosmo_choices)
    visio = models.BooleanField(default=False)

    def __str__(self):
        text = f"Dept {self.department.abbrev}: "
        if not self.cosmo:
            text += "educational mode "
        else:
            text += f"cosmo{self.cosmo} mode "
        if self.visio:
            text += "with "
        else:
            text += "without "
        text += "visio."
        return text


@receiver(post_save, sender=Department)
def create_department_related(sender, instance, created, raw, **kwargs):
    if not created or raw:
        return

    Mode.objects.create(department=instance)
    TimeGeneralSettings.objects.create(
        department=instance,
        day_start_time=6 * 60,
        day_finish_time=20 * 60,
        lunch_break_start_time=13 * 60,
        lunch_break_finish_time=13 * 60,
        days=days_list
    )


# </editor-fold>

# <editor-fold desc="ROOMS">
# -----------
# -- ROOMS --
# -----------


class RoomType(models.Model):
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    def basic_rooms(self):
        s = set(b for r in self.members.all() for b in r.and_subrooms() if b.is_basic)
        return s


class RoomAttribute(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField(null=True)

    def is_boolean(self):
        return hasattr(self, "booleanroomattribute")

    def is_numeric(self):
        return hasattr(self, "numericroomattribute")

    def __str__(self):
        return self.name


class BooleanRoomAttribute(RoomAttribute):
    attribute = models.OneToOneField(RoomAttribute, parent_link=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name + ' (boolean)'


class NumericRoomAttribute(RoomAttribute):
    attribute = models.OneToOneField(RoomAttribute, parent_link=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name + ' (numeric)'


class BooleanRoomAttributeValue(models.Model):
    room = models.ForeignKey('Room', on_delete=models.CASCADE)
    attribute = models.ForeignKey('BooleanRoomAttribute', on_delete=models.CASCADE)
    value = models.BooleanField()


class NumericRoomAttributeValue(models.Model):
    room = models.ForeignKey('Room', on_delete=models.CASCADE)
    attribute = models.ForeignKey('NumericRoomAttribute', on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=7, decimal_places=2)


class Room(models.Model):
    name = models.CharField(max_length=50)
    types = models.ManyToManyField(RoomType,
                                   blank=True,
                                   related_name="members")
    subroom_of = models.ManyToManyField('self',
                                        symmetrical=False,
                                        blank=True,
                                        related_name="subrooms")
    departments = models.ManyToManyField(Department)

    @property
    def is_basic(self):
        return self.subrooms.count() == 0

    def and_subrooms(self):
        ret = {self}
        for sub in self.subrooms.all():
            ret |= sub.and_subrooms()
        return ret

    def basic_rooms(self):
        s = set(r for r in self.and_subrooms() if r.is_basic)
        return s

    def and_overrooms(self):
        ret = {self}
        for over in self.subroom_of.all():
            ret |= over.and_overrooms()
        return ret

    def __str__(self):
        return self.name

    def str_extended(self):
        return f'{self.name}, ' \
               + f'Types: {[t.name for t in self.types.all()]}, ' \
               + f'Depts: {self.departments.all()}, ' \
               + f'Is in: {[rg.name for rg in self.subroom_of.all()]}'


class RoomSort(models.Model):
    for_type = models.ForeignKey(RoomType, blank=True, null=True,
                                 related_name='+', on_delete=models.CASCADE)
    prefer = models.ForeignKey(Room, blank=True, null=True,
                               related_name='+', on_delete=models.CASCADE)
    unprefer = models.ForeignKey(Room, blank=True, null=True,
                                 related_name='+', on_delete=models.CASCADE)
    tutor = models.ForeignKey('people.Tutor',
                              related_name='abcd',
                              null=True,
                              default=None,
                              on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.for_type}: {self.tutor} prefers {self.prefer} to {self.unprefer}"


class RoomPonderation(models.Model):
    department = models.ForeignKey('Department', on_delete=models.CASCADE)
    room_types = ArrayField(models.PositiveSmallIntegerField())
    ponderations = ArrayField(models.PositiveSmallIntegerField(), null=True)
    basic_rooms = models.ManyToManyField('Room')

    def save(self, *args, **kwargs):
        super(RoomPonderation, self).save(*args, **kwargs)
        self.add_basic_rooms()

    def add_basic_rooms(self):
        RT = RoomType.objects.filter(id__in=self.room_types)
        for rt in RT:
            for basic_room in rt.basic_rooms():
                self.basic_rooms.add(basic_room)

    def get_room_types_set(self):
        return set(RoomType.objects.filter(id__in=self.room_types))


# </editor-fold>

# <editor-fold desc="COURSES">
# -------------
# -- COURSES --
# -------------


class Module(models.Model):
    name = models.CharField(max_length=200, null=True)
    abbrev = models.CharField(max_length=100, verbose_name=_('Abbreviation'))
    head = models.ForeignKey('people.Tutor',
                             null=True,
                             default=None,
                             blank=True,
                             on_delete=models.CASCADE,
                             verbose_name='responsable')
    ppn = models.CharField(max_length=30, default='M')
    train_prog = models.ForeignKey(
        'TrainingProgramme', on_delete=models.CASCADE)
    period = models.ForeignKey('Period', on_delete=models.CASCADE)
    url = models.URLField(null=True, blank=True, default=None)
    description = models.TextField(null=True, blank=True, default=None)

    def __str__(self):
        return self.abbrev

    class Meta:
        ordering = ['abbrev', ]


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
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, null=True)
    duration = models.PositiveSmallIntegerField(default=90)
    pay_duration = models.PositiveSmallIntegerField(null=True, blank=True)
    group_types = models.ManyToManyField(GroupType,
                                         blank=True,
                                         related_name="compatible_course_types")
    graded = models.BooleanField(verbose_name=_('graded?'), default=False)

    def __str__(self):
        return self.name


class Course(models.Model):
    type = models.ForeignKey('CourseType', on_delete=models.CASCADE)
    room_type = models.ForeignKey(
        'RoomType', null=True, on_delete=models.CASCADE)
    tutor = models.ForeignKey('people.Tutor',
                              related_name='taught_courses',
                              null=True,
                              blank=True,
                              default=None,
                              on_delete=models.CASCADE)
    supp_tutor = models.ManyToManyField('people.Tutor',
                                        related_name='courses_as_supp',
                                        blank=True)
    groups = models.ManyToManyField('base.GenericGroup', related_name='courses', blank=True)
    module = models.ForeignKey(
        'Module', related_name='courses', on_delete=models.CASCADE)
    modulesupp = models.ForeignKey('Module', related_name='courses_as_modulesupp',
                                   null=True, blank=True, on_delete=models.CASCADE)
    pay_module = models.ForeignKey('Module', related_name='courses_as_pay_module',
                                   null=True, blank=True, on_delete=models.CASCADE)
    week = models.ForeignKey('Week', on_delete=models.CASCADE, null=True, blank=True)
    suspens = models.BooleanField(verbose_name=_('Suspens?'), default=False)
    show_id = False

    def __str__(self):
        username_mod = self.tutor.username if self.tutor is not None else '-no_tut-'
        return f"{self.type}-{self.module}-{username_mod}-{'|'.join([g.name for g in self.groups.all()])}" \
               + (" (%s)" % self.id if self.show_id else "")

    def full_name(self):
        username_mod = self.tutor.username if self.tutor is not None else '-no_tut-'
        return f"{self.type}-{self.module}-{username_mod}-{'|'.join([g.name for g in self.groups.all()])}"

    def equals(self, other):
        return self.__class__ == other.__class__ \
               and self.type == other.type \
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
    visio_preference_value = models.SmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(8)],
                                                      default=1)


class CoursePossibleTutors(models.Model):
    course = models.OneToOneField('Course', on_delete=models.CASCADE)
    possible_tutors = models.ManyToManyField(
        'people.Tutor', blank=True, related_name='shared_possible_courses')


class ScheduledCourse(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    day = models.CharField(
        max_length=2, choices=Day.CHOICES, default=Day.MONDAY)
    # in minutes from 12AM
    start_time = models.PositiveSmallIntegerField()
    room = models.ForeignKey(
        'Room', blank=True, null=True, on_delete=models.SET_NULL)
    number = models.PositiveSmallIntegerField(null=True, blank=True)
    noprec = models.BooleanField(
        verbose_name='vrai si on ne veut pas garder la salle', default=True)
    work_copy = models.PositiveSmallIntegerField(default=0)
    tutor = models.ForeignKey('people.Tutor',
                              related_name='taught_scheduled_courses',
                              null=True,
                              default=None,
                              on_delete=models.SET_NULL)

    # les utilisateurs auront acces à la copie publique (0)

    def __str__(self):
        return f"{self.course}{self.number}:{self.day}-t{self.start_time}-{self.room}"

    def unique_name(self):
        return f"{self.course.type}_{self.room}_{self.tutor.username}_{self.day}_{self.start_time}_{self.end_time}"

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
    scheduled_course = models.OneToOneField(
        'ScheduledCourse',
        on_delete=models.CASCADE,
        related_name='additional')
    link = models.ForeignKey(
        'EnrichedLink',
        blank=True, null=True, default=None,
        related_name='additional',
        on_delete=models.SET_NULL)
    comment = models.CharField(
        max_length=100,
        null=True, default=None, blank=True)

    def __str__(self):
        resp = '{' + str(self.scheduled_course) + '}'
        if self.link.description:
            resp += '[' + str(self.link.description) + ']'
        if self.comment:
            resp += '(' + str(self.comment) + ')'
        return resp


class EnrichedLink(models.Model):
    url = models.URLField()
    description = models.CharField(max_length=100,
                                   null=True, default=None, blank=True)

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
    group = models.OneToOneField('base.StructuralGroup',
                                 on_delete=models.CASCADE,
                                 related_name='preferred_links')
    links = models.ManyToManyField('EnrichedLink',
                                   related_name='group_set')

    def __str__(self):
        return self.group.full_name + ' : ' + \
               ' ; '.join([str(l) for l in self.links.all()])


# </editor-fold desc="COURSES">

# <editor-fold desc="PREFERENCES">
# -----------------
# -- PREFERENCES --
# -----------------

class Preference(models.Model):
    start_time = models.PositiveSmallIntegerField()
    duration = models.PositiveSmallIntegerField()
    week = models.ForeignKey('Week', on_delete=models.CASCADE, null=True, blank=True)
    day = models.CharField(
        max_length=2, choices=Day.CHOICES, default=Day.MONDAY)
    value = models.SmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(8)],
        default=8)
    class Meta:
        abstract = True

    @property
    def end_time(self):
        return self.start_time + self.duration


class UserPreference(Preference):
    user = models.ForeignKey('people.Tutor', on_delete=models.CASCADE)

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

    def __str__(self):
        return f"{self.course_type}=Sem{self.week}:" + \
               f"({str_slot(self.day, self.start_time, self.duration)})" + \
               f"--{self.train_prog}={self.value}"


class RoomPreference(Preference):
    room = models.ForeignKey(
        'Room', on_delete=models.CASCADE, default=None, null=True)

    def __str__(self):
        return f"{self.room}-Sem{self.week}:" + \
               f"({str_slot(self.day, self.start_time, self.duration)})" + \
               f"={self.value}"


# </editor-fold desc="PREFERENCES">

# <editor-fold desc="MODIFICATIONS">
# -----------------
# - MODIFICATIONS -
# -----------------


class EdtVersion(models.Model):
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, null=True)
    week = models.ForeignKey('Week', on_delete=models.CASCADE, null=True, blank=True)
    version = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = (("department", "week"),)


#    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


# null iff no change
class CourseModification(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    old_week = models.ForeignKey('Week', on_delete=models.CASCADE, null=True, blank=True)
    room_old = models.ForeignKey(
        'Room', blank=True, null=True, on_delete=models.CASCADE)
    day_old = models.CharField(
        max_length=2, choices=Day.CHOICES, default=None, null=True)
    start_time_old = models.PositiveSmallIntegerField(default=None, null=True)
    tutor_old = models.ForeignKey('people.Tutor',
                                  related_name='impacted_by_course_modif',
                                  null=True,
                                  default=None,
                                  on_delete=models.SET_NULL)
    version_old = models.PositiveIntegerField()
    updated_at = models.DateTimeField(auto_now=True)
    initiator = models.ForeignKey('people.User', on_delete=models.CASCADE)

    def strs_course_changes(self, course=None, sched_course=None):
        if course is None:
            course = self.course
        if sched_course is None:
            sched_course = ScheduledCourse.objects.get(
                course=course, work_copy=0)
        department = course.type.department
        al = '\n  · '
        same = f'- Cours {course.module.abbrev} semaine {course.week}'
        changed = ''

        tutor_old_name = self.tutor_old.username if self.tutor_old is not None else "personne"
        if sched_course.tutor == self.tutor_old:
            same += f', par {tutor_old_name}'
        else:
            cur_tutor_name = sched_course.tutor.username if sched_course.tutor is not None else "personne"
            changed += al + f'Prof : {tutor_old_name} -> {cur_tutor_name}'

        if sched_course.room is None:
            if ScheduledCourseAdditional.objects.filter(scheduled_course=sched_course).exists():
                cur_room_name = "en visio"
            else:
                cur_room_name = "nulle part"
        else:
            cur_room_name = sched_course.room.name

        if sched_course.room == self.room_old:
            same += f', {cur_room_name}'
        else:
            room_old_name = self.room_old.name if self.room_old is not None else "sans salle"
            changed += al + f'Salle : {room_old_name} -> {cur_room_name}'

        day_list = base.weeks.num_all_days(
            course.week.year, course.week.nb, department)
        if sched_course.day == self.day_old \
                and sched_course.start_time == self.start_time_old:
            for d in day_list:
                if d['ref'] == sched_course.day:
                    day = d
            same += f', {day["name"]} {day["date"]} à {hhmm(sched_course.start_time)}'
        else:
            changed += al + 'Horaire : '
            if self.day_old is None or self.start_time_old is None:
                changed += 'non placé'
            else:
                for d in day_list:
                    if d['ref'] == self.day_old:
                        day = d
                changed += f'{day["name"]} {day["date"]} à {hhmm(self.start_time_old)}'
            changed += ' -> '
            for d in day_list:
                if d['ref'] == sched_course.day:
                    day = d
            changed += f'{day["name"]} {day["date"]} à {hhmm(sched_course.start_time)}'

        return same, changed

    def __str__(self):
        same, changed = self.strs_course_changes()
        if self.version_old is not None:
            same += f' ; (NumV {self.version_old})'
        ret = same + changed + \
              f"\n  by {self.initiator.username}, at {self.updated_at}"
        return ret


# </editor-fold desc="MODIFICATIONS">

# <editor-fold desc="COSTS">
# -----------
# -- COSTS --
# -----------


class TutorCost(models.Model):
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, null=True)
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


# </editor-fold desc="COSTS">


# <editor-fold desc="MISC">
# ----------
# -- MISC --
# ----------


class Dependency(models.Model):
    course1 = models.ForeignKey(
        'Course', related_name='first_course', on_delete=models.CASCADE)
    course2 = models.ForeignKey(
        'Course', related_name='second_course', on_delete=models.CASCADE)
    successive = models.BooleanField(verbose_name=_('Successives?'), default=False)
    ND = models.BooleanField(verbose_name=_('On different days'), default=False)
    day_gap = models.PositiveSmallIntegerField(verbose_name=_('Minimal day gap between courses'), default=0)

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
        models.PositiveSmallIntegerField(), blank=True)


class Regen(models.Model):
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, null=True)
    week = models.ForeignKey('Week', on_delete=models.CASCADE, null=True, blank=True)
    full = models.BooleanField(verbose_name=_('Full'),
                               default=True)
    fdate = models.DateField(verbose_name=_('Full generation date'), null=True, blank=True)
    stabilize = models.BooleanField(verbose_name=_('Stabilized'),
                                    default=False)
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

# </editor-fold desc="MISC">
