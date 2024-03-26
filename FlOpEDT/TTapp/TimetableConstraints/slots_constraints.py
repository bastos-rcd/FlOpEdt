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


import datetime as dt

from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

import TTapp.global_pre_analysis.partition_with_constraints as partition_bis
from base.models import CourseStartTimeConstraint, Dependency
from base.timing import Day, slot_pause
from core.decorators import timer
from TTapp.ilp_constraints.constraint import Constraint
from TTapp.ilp_constraints.constraint_type import ConstraintType
from TTapp.ilp_constraints.constraints.dependencyConstraint import DependencyConstraint
from TTapp.slots import Slot, days_filter, slots_filter
from TTapp.TimetableConstraints.core_constraints import ConsiderTutorsUnavailability
from TTapp.TimetableConstraints.TimetableConstraint import TimetableConstraint
from TTapp.TimetableConstraints.tutors_constraints import considered_tutors


class SimultaneousCourses(TimetableConstraint):
    """
    Force courses to start simultaneously
    """

    courses = models.ManyToManyField(
        "base.Course", related_name="simultaneous_courses_constraints"
    )

    def pre_analyse(self, period):
        """
        Pre-analysis of the constraint
        Firstly verify if there is only one course per group/tutor to be done simultaneously
        Then built a partition comparing each tutor availability (Can be optimized)
        At the end, try to find an available slot in the period for the considered_courses

        Parameters :
            period : pre_analyse's current period

        Returns :
            jsondict :  a Json dictionary that contains the result of the pre-analyse
        """
        jsondict = {
            "status": _("OK"),
            "messages": [],
            "period": {"id": period.id, "name": period.name},
        }

        # pre_analyse's period simultaneous courses retrieval
        considered_courses = list(c for c in self.courses.all() if c.period == period)

        # We verify if there is only one course to do simultaneously for each tutor/group
        jsondict, OK = self.maxOneCourse(jsondict, considered_courses)
        if not (OK):
            return jsondict

        # No course in the constraint case
        if len(considered_courses) == 0:
            jsondict["status"] = _("KO")
            message = gettext(
                "No partition created : maybe there is no courses or it's wrong the period"
            )
            jsondict["messages"].append({"str": message, "type": "SimultaneousCourses"})
            return jsondict

        # We build a period's partition comparing partition of each tutors
        partition = None
        no_user_pref = not ConsiderTutorsUnavailability.objects.filter(
            periods=period
        ).exists()
        for course in considered_courses:
            if partition == None:  # Here we build the partition of the first teacher
                partition = partition_bis.create_course_partition_from_constraints(
                    course, period, course.type.department, available=no_user_pref
                )
            new_partition = partition_bis.create_course_partition_from_constraints(
                course, period, course.type.department, available=no_user_pref
            )
            """
            Then, for each interval (named interval1) available and not forbidden of the main partition (named partition) 
            we watch if the interval of another teacher (named interval2) is also available and not forbidden 
            """
            for interval1 in partition.intervals:
                if interval1[1]["available"] and not (interval1[1]["forbidden"]):
                    for interval2 in new_partition.intervals:
                        if not (
                            interval1[0].start >= interval2[0].end
                            or interval1[0].end <= interval2[0].start
                        ):
                            interval1[1]["available"] = interval2[1]["available"]
                            interval1[1]["forbidden"] = interval2[1]["forbidden"]

        max_duration = 0
        # Here we find the maximal duration of the simultaneous courses
        for course in considered_courses:
            max_duration = max(max_duration, course.duration)

        # Here we search for an available slot in the period
        if partition.nb_slots_available_of_duration(max_duration) < 1:
            jsondict["status"] = _("KO")
            message = gettext("Not enough common available time for courses ")
            for course in considered_courses:
                message += " {course} "
            message += " to be done simultaneously"
            jsondict["messages"].append({"str": message, "type": "SimultaneousCourses"})
            jsondict["status"] = _("KO")
        return jsondict

    def maxOneCourse(self, jsondict, consideredCourses):
        """Verify that tutors and groups have only one course to do simultaneously
        Parameters :
            jsondict : a Json dictionary
            consideredCourses : The considered courses to be done simultaneously

        Returns :
            jsondict :  a Json dictionary
            statusOK : boolean, True if it's all good, False otherwise
        Limit start time choice
        """
        consideredTutors = []
        consideredGroups = []
        tutorError = []
        groupError = []
        statusOK = True
        for course in consideredCourses:
            if consideredTutors.__contains__(course.tutor):
                if not (tutorError.__contains__(course.tutor)):
                    tutorError.append(course.tutor)
                    jsondict["status"] = _("KO")
                    message = (
                        gettext("Tutor %s has more than one to do at the same time")
                        % course.tutor
                    )
                    jsondict["messages"].append(
                        {
                            "str": message,
                            "tutor": course.tutor.id,
                            "type": "SimultaneousCourses",
                        }
                    )
                    statusOK = False
            consideredTutors.append(course.tutor)
            course_groups = course.groups.all()
            for group in course_groups:
                if consideredGroups.__contains__(group):
                    if not (groupError.__contains__(group)):
                        groupError.append(group)
                        jsondict["status"] = _("KO")
                        message = (
                            gettext(
                                "Group %s has more than one course to do at the same time"
                            )
                            % group.name
                        )
                        jsondict["messages"].append(
                            {
                                "str": message,
                                "group": group.id,
                                "type": "SimultaneousCourses",
                            }
                        )
                        statusOK = False
                consideredGroups.append(group)
        return jsondict, statusOK

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        courses_periods = self.courses.all().distinct("period")
        nb = courses_periods.count()
        if nb == 0:
            return
        else:
            super().save(*args, **kwargs)
            self.periods.clear()
            for w in courses_periods:
                self.periods.add(w.period)

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(["courses"])
        return attributes

    def enrich_ttmodel(self, ttmodel, period, ponderation=1):
        course_types = set(c.type for c in self.courses.all())
        relevant_courses = set(self.courses.all()) & set(ttmodel.data.courses)
        nb_courses = len(relevant_courses)
        if nb_courses < 2:
            return
        possible_start_times = set()
        for t in course_types:
            possible_start_times |= set(
                t.coursestarttimeconstraint_set.all()[0].allowed_start_times
            )
        for day in days_filter(ttmodel.data.days, period=period):
            for st in possible_start_times:
                check_var = ttmodel.add_var("check_var")
                expr = ttmodel.lin_expr()
                for c in relevant_courses:
                    possible_slots = slots_filter(
                        ttmodel.data.compatible_slots[c], start_time=st, day=day
                    )
                    for sl in possible_slots:
                        expr += ttmodel.scheduled[(sl, c)]
                ttmodel.add_constraint(
                    nb_courses * check_var - expr,
                    "==",
                    0,
                    Constraint(
                        constraint_type=ConstraintType.SIMULTANEOUS_COURSES,
                        courses=relevant_courses,
                    ),
                )
                ttmodel.add_constraint(
                    expr - check_var,
                    ">=",
                    0,
                    Constraint(
                        constraint_type=ConstraintType.SIMULTANEOUS_COURSES,
                        courses=relevant_courses,
                    ),
                )

    def get_viewmodel(self):
        view_model = super().get_viewmodel()
        details = view_model["details"]

        if self.courses.exists():
            details.update(
                {"courses": ", ".join([str(course) for course in self.courses.all()])}
            )

        return view_model

    def one_line_description(self):
        return f"Les cours {self.courses.all()} doivent être simultanés !"

    class Meta:
        verbose_name = _("Simultaneous courses")
        verbose_name_plural = verbose_name


class StartTimeConstraint(TimetableConstraint):
    train_progs = models.ManyToManyField("base.TrainingProgramme", blank=True)
    module = models.ForeignKey(
        "base.Module", null=True, blank=True, default=None, on_delete=models.CASCADE
    )
    tutor = models.ForeignKey(
        "people.Tutor", null=True, blank=True, default=None, on_delete=models.CASCADE
    )
    group = models.ForeignKey(
        "base.StructuralGroup",
        null=True,
        blank=True,
        default=None,
        on_delete=models.CASCADE,
    )
    course_type = models.ForeignKey(
        "base.CourseType", null=True, blank=True, default=None, on_delete=models.CASCADE
    )

    class Meta:
        abstract = True

    def excluded_slots(self, ttmodel):
        raise NotImplementedError

    def enrich_ttmodel(self, ttmodel, period, ponderation=1.0):
        fc = self.get_courses_queryset_by_attributes(period, ttmodel)
        excluded_slots = self.excluded_slots(ttmodel)
        if self.tutor is None:
            relevant_sum = ttmodel.sum(
                ttmodel.scheduled[(sl, c)]
                for c in fc
                for sl in ttmodel.data.compatible_slots[c] & excluded_slots
            )
        else:
            relevant_sum = ttmodel.sum(
                ttmodel.assigned[(sl, c, self.tutor)]
                for c in fc
                for sl in ttmodel.data.compatible_slots[c] & excluded_slots
            )
        if self.weight is not None:
            ttmodel.add_to_generic_cost(
                self.local_weight() * ponderation * relevant_sum, period=period
            )
        else:
            ttmodel.add_constraint(
                relevant_sum,
                "==",
                0,
                Constraint(
                    constraint_type=ConstraintType.LIMITED_START_TIME_CHOICES,
                    instructors=self.tutor,
                    groups=self.group,
                    modules=self.module,
                ),
            )


class LimitStartTimeChoices(StartTimeConstraint):
    """
    Limit the possible start times
    """

    possible_week_days = ArrayField(
        models.CharField(max_length=2, choices=Day.CHOICES), blank=True, null=True
    )
    possible_start_times = ArrayField(models.TimeField(), blank=True, null=True)

    class Meta:
        verbose_name = _("Limited start time choices")
        verbose_name_plural = verbose_name

    def considered_start_times(self, ttmodel):
        if self.possible_start_times:
            return self.possible_start_times
        return set(sl.start_time.time() for sl in ttmodel.data.courses_slots)

    def considered_week_days(self):
        if self.possible_week_days:
            return self.possible_week_days
        return list(c[0] for c in Day.CHOICES)

    def excluded_slots(self, ttmodel):
        return set(
            sl
            for sl in ttmodel.data.courses_slots
            if (
                sl.start_time.time() not in self.considered_start_times(ttmodel)
                or sl.start_time.date().day not in self.considered_week_days()
            )
        )

    def one_line_description(self):
        text = "Les "
        if self.course_type:
            text += str(self.course_type)
        else:
            text += "cours"
        if self.module:
            text += " de " + str(self.module)
        if self.tutor:
            text += " de " + str(self.tutor)
        if self.train_progs.exists():
            text += " en " + ", ".join(
                [train_prog.abbrev for train_prog in self.train_progs.all()]
            )
        else:
            text += " pour toutes les promos"
        if self.group:
            text += " avec le groupe " + str(self.group)
        text += " ne peuvent avoir lieu que"
        if not (self.possible_week_days or self.possible_start_times):
            text += " ... Tout le temps!"
        else:
            if self.possible_week_days:
                text += " les "
                text += ", ".join(self.possible_week_days)
            if self.possible_start_times:
                text += " à "
                text += ", ".join([pst for pst in self.possible_start_times])
        text += "."
        return text


class AvoidStartTimes(StartTimeConstraint):
    """
    Avoid some start times
    """

    forbidden_week_days = ArrayField(
        models.CharField(max_length=2, choices=Day.CHOICES), blank=True, null=True
    )
    forbidden_start_times = ArrayField(models.TimeField(), blank=True, null=True)

    class Meta:
        verbose_name = _("Avoid considered start times")
        verbose_name_plural = verbose_name

    def considered_start_times(self, ttmodel):
        if self.forbidden_start_times:
            return self.forbidden_start_times
        return set(sl.start_time.time() for sl in ttmodel.data.courses_slots)

    def considered_week_days(self):
        if self.forbidden_week_days:
            return self.forbidden_week_days
        return list(c[0] for c in Day.CHOICES)

    def excluded_slots(self, ttmodel):
        return set(
            sl
            for sl in ttmodel.data.courses_slots
            if (
                sl.start_time.time() in self.considered_start_times(ttmodel)
                and sl.day.day in self.considered_week_days()
            )
        )

    def one_line_description(self):
        text = "Les "
        if self.course_type:
            text += str(self.course_type)
        else:
            text += "cours"
        if self.module:
            text += " de " + str(self.module)
        if self.tutor:
            text += " de " + str(self.tutor)
        if self.train_progs.exists():
            text += " en " + ", ".join(
                [train_prog.abbrev for train_prog in self.train_progs.all()]
            )
        else:
            text += " pour toutes les promos"
        if self.group:
            text += " avec le groupe " + str(self.group)
        text += " ne peuvent pas avoir lieu"
        if not (self.forbidden_week_days or self.forbidden_start_times):
            text += " ... Tout le temps!"
        else:
            if self.forbidden_week_days:
                text += " les "
                text += ", ".join(self.forbidden_week_days)
            if self.forbidden_week_days:
                text += " à "
                text += ", ".join([fst for fst in self.forbidden_start_times])
        text += "."
        return text


################    ConsiderDependencies FUNCTIONS      ################
def find_successive_slots(
    course_slot1, course_slot2, course1_duration, course2_duration
):
    """This function returns True if it finds a slot for the second course right after one of the first one with enough
    time duration.
    Complexity on O(n^2): n being the number of slots for each course.

    Parameters:
        course_slot1 (list(TimeInterval)): A list of time interval representing when the first course can be placed
        course_slot2 (list(TimeInterval)): A list of time interval representing when the second course can be placed
        course1_duration (dt.timedelta): The duration of the first course
        course2_duration (dt.timedelta): The duration of the second course

    Returns:
        (boolean): If we found at least one eligible slot"""
    for cs1 in course_slot1:
        possible_start_time = cs1.start + course1_duration
        for cs2 in course_slot2:
            if cs2.start <= cs1.end:
                if (
                    cs2.start > possible_start_time
                    and cs2.end >= cs2.start + course2_duration
                ):
                    return True
                elif (
                    cs2.start <= possible_start_time
                    and cs2.end >= possible_start_time + course2_duration
                ):
                    return True
            if cs2.start > possible_start_time:
                break
    return False


def find_day_gap_slots(course_slots1, course_slots2, day_gap):
    """This function search in the available times for each course if we can find a slot for the second course after a day gap passed
    in the parameters.

    Parameters:
        course_slots1 (list(TimeInterval)): The TimeIntervals (starting datetime and ending datetime) available for the first course
        course_slots2 (list(TimeInterval)): The TimeIntervals (starting datetime and ending datetime) available for the second course
        day_gap (int): The number of days between the two courses

    Returns:
        (boolean) : whether there is available time for the second course after the day gap or not
    """
    day_slot = (
        course_slots1[0].start
        + dt.timedelta(days=day_gap)
        - dt.timedelta(
            hours=course_slots1[0].start.hour, minutes=course_slots1[0].start.minute
        )
    )
    for cs2 in course_slots2:
        if cs2.start > day_slot:
            return True
    return False


class GlobalModuleDependency(TimetableConstraint):
    """
    Creates a global dependency for each group and module between courses1 and courses2
    """

    modules = models.ManyToManyField(
        "base.Module", related_name="global_module_dependencies", blank=True
    )
    train_progs = models.ManyToManyField("base.TrainingProgramme", blank=True)
    groups = models.ManyToManyField(
        "base.StructuralGroup", related_name="global_dependency_groups", blank=True
    )
    day_gap = models.PositiveSmallIntegerField(
        verbose_name=_("Minimal day gap between courses"), default=0
    )
    course1_type = models.ForeignKey(
        "base.CourseType",
        related_name="global_dependency_course1_type",
        null=True,
        blank=True,
        default=None,
        on_delete=models.CASCADE,
    )

    course1_tutor = models.ForeignKey(
        "people.Tutor",
        related_name="global_dependency_course1_tutor",
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET_NULL,
    )
    course2_type = models.ForeignKey(
        "base.CourseType",
        related_name="global_dependency_course2_type",
        null=True,
        blank=True,
        default=None,
        on_delete=models.CASCADE,
    )
    course2_tutor = models.ForeignKey(
        "people.Tutor",
        related_name="global_dependency_course2_tutor",
        null=True,
        blank=True,
        default=None,
        on_delete=models.CASCADE,
    )

    def one_line_description(self):
        if self.modules.exists():
            text = f"Pour chacun des modules {self.modules.all()}, les cours"
        else:
            text = "Pour tous les modules, les cours"
        if self.course1_type:
            text += f" de type {self.course1_type}"
        if self.course1_tutor:
            text += f" du prof {self.course1_tutor}"
        text += " doivent être faits"
        if self.day_gap:
            text += f" au moins {self.day_gap} jours"
        text += " avant les autres cours"
        if self.course2_type:
            text += f" de type {self.course1_type}"
        if self.course2_tutor:
            text += f" du prof {self.course1_tutor}"

    def considered_courses_tuple(self, period, ttmodel=None):
        """Returns the tuple courses1, courses2 of courses that have to be considered"""
        courses1 = self.get_courses_queryset_by_parameters(
            period,
            ttmodel=ttmodel,
            course_type=self.course1_type,
            modules=self.modules.all(),
            tutor=self.course1_tutor,
            train_progs=self.train_progs,
            groups=self.groups,
        )
        courses2 = self.get_courses_queryset_by_parameters(
            period,
            ttmodel=ttmodel,
            course_type=self.course2_type,
            modules=self.modules.all(),
            tutor=self.course2_tutor,
            train_progs=self.train_progs,
            groups=self.groups,
        )
        return courses1, courses2

    def enrich_ttmodel(self, ttmodel, period, ponderation=1):
        courses1, courses2 = self.considered_courses_tuple(period, ttmodel)
        a_lot = 1000000
        for g in self.considered_basic_groups(ttmodel):
            group_courses1 = courses1.filter(groups__in=g.connected_groups())
            group_courses2 = courses2.filter(groups__in=g.connected_groups())
            for c1 in group_courses1:
                for sl1 in ttmodel.data.compatible_slots[c1]:
                    if not self.weight:
                        ttmodel.add_constraint(
                            a_lot * ttmodel.scheduled[(sl1, c1)]
                            + ttmodel.sum(
                                ttmodel.scheduled[(sl2, c2)]
                                for c2 in group_courses2.exclude(id=c1.id)
                                for sl2 in ttmodel.data.compatible_slots[c2]
                                if not sl2.is_after(sl1)
                                or (sl2.day - sl1.day).days < self.day_gap
                            ),
                            "<=",
                            a_lot,
                            Constraint(
                                constraint_type=ConstraintType.DEPENDANCE,
                                slots=sl1,
                                modules=self.modules.all(),
                                groups=g,
                            ),
                        )
                    else:
                        for c2 in group_courses2:
                            for sl2 in ttmodel.data.compatible_slots[c2]:
                                if (
                                    not sl2.is_after(sl1)
                                    or (sl2.day - sl1.day).days < self.day_gap
                                ):
                                    conj_var = ttmodel.add_conjunct(
                                        ttmodel.scheduled[(sl1, c1)],
                                        ttmodel.scheduled[(sl2, c2)],
                                    )
                                    ttmodel.add_to_generic_cost(
                                        conj_var * self.local_weight() * ponderation
                                    )

    def is_satisfied_for(self, period, version):
        courses1, courses2 = self.considered_courses_tuple(period)
        dependency_not_satisfied_for = []
        for g in self.considered_basic_groups():
            group_courses1 = courses1.filter(groups__in=g.connected_groups())
            group_courses2 = courses2.filter(groups__in=g.connected_groups())
            for c1 in group_courses1:
                if not c1.scheduledcourse_set.filter(version=version).exists():
                    continue
                for c2 in group_courses2.exclude(id=c1.id):
                    if not c2.scheduledcourse_set.filter(version=version).exists():
                        continue
                    sched_course1 = c1.scheduledcourse_set.get(version=version)
                    sched_course2 = c2.scheduledcourse_set.get(version=version)
                    if (
                        sched_course2.start_time <= sched_course1.start_time
                        or (
                            sched_course2.start_time.date
                            - sched_course1.start_time.date
                        ).days
                        < self.day_gap
                    ):
                        dependency_not_satisfied_for.append(c1)
        assert (
            not dependency_not_satisfied_for
        ), f"Following courses do not respect global dependency :{dependency_not_satisfied_for}"


class ConsiderDependencies(TimetableConstraint):
    """
    Transform the constraints of dependency saved on the DB in model constraints:
    -include dependencies and successiveness
    -include non same-day constraint
    -include simultaneity (double dependency)
    If there is a weight, it's a preference, else it's a constraint...
    """

    train_progs = models.ManyToManyField("base.TrainingProgramme", blank=True)
    modules = models.ManyToManyField("base.Module", blank=True)

    class Meta:
        verbose_name = _("Consider dependecies")
        verbose_name_plural = verbose_name

    @timer
    def pre_analyse(self, period):
        """Pre analysis of the Constraint
        For each dependency, first checks if there is available slots for both courses taking in consideration tutor's and supp_tutor's
        availabilities, NoTutorCourseOnDay constraints and possible start times. Then we check if we still have slots for the second one
        starting after the first one and then if the options are True and or above 0 we check successive slots and the day gap.

        Parameter:
            period (SchedulingPeriod): the period we want to analyse the data from

        Returns:
            JsonResponse: with status 'KO' or 'OK' and a list of messages explaining the problem
        """
        dependencies = self.considered_dependecies().filter(
            course1__period=period, course2__period=period
        )
        jsondict = {
            "status": _("OK"),
            "messages": [],
            "period": {"id": period.id, "name": period.name},
        }
        no_user_pref1 = no_user_pref2 = not ConsiderTutorsUnavailability.objects.filter(
            Q(periods=period) | Q(periods__isnull=True)
        ).exists()
        for dependency in dependencies:
            ok_so_far = True
            # Setting up partitions with data about other constraints for both courses
            if dependency.course1.tutor is None:
                no_user_pref1 = True
            if dependency.course2.tutor is None:
                no_user_pref2 = True

            period_partition_course1 = (
                partition_bis.create_course_partition_from_constraints(
                    dependency.course1, period, self.department, available=no_user_pref1
                )
            )
            period_partition_course2 = (
                partition_bis.create_course_partition_from_constraints(
                    dependency.course2, period, self.department, available=no_user_pref2
                )
            )

            if period_partition_course1 and period_partition_course2:
                # Retrieving possible start times for both courses
                course1_start_times = CourseStartTimeConstraint.objects.get(
                    course_type=dependency.course1.type
                ).allowed_start_times
                course2_start_times = CourseStartTimeConstraint.objects.get(
                    course_type=dependency.course2.type
                ).allowed_start_times
                # Retrieving only TimeInterval for each course
                course1_slots = period_partition_course1.find_all_available_timeinterval_starting_at(
                    course1_start_times, dependency.course1.duration
                )
                course2_slots = period_partition_course2.find_all_available_timeinterval_starting_at(
                    course2_start_times, dependency.course2.duration
                )
                if course1_slots and course2_slots:
                    while (
                        course2_slots[0].end
                        < course1_slots[0].start
                        + dependency.course1.duration
                        + dependency.course2.duration
                    ):
                        course2_slots.pop(0)
                        if not course2_slots:
                            break
                    if course2_slots:
                        if (
                            course1_slots[0].start + dependency.course1.duration
                            > course2_slots[0].start
                        ):
                            course2_slots[0].start = (
                                course1_slots[0].start + dependency.course1.duration
                            )
                        # Here we check if the first course_slot that we might just shrank is still long enough and if it is the only
                        # one left.
                        if (
                            len(course2_slots) <= 1
                            and course2_slots[0].duration < dependency.course2.duration
                        ):
                            jsondict["status"] = _("KO")
                            ok_so_far = False
                            jsondict["messages"].append(
                                {
                                    "str": gettext(
                                        "There is no available slots for the second course after the first one : %s"
                                    )
                                    % dependency,
                                    "course1": dependency.course1.id,
                                    "course2": dependency.course2.id,
                                    "type": "ConsiderDependencies",
                                }
                            )
                    else:
                        jsondict["status"] = _("KO")
                        ok_so_far = False
                        jsondict["messages"].append(
                            {
                                "str": gettext(
                                    "There is no available slots for the second course after the first one : %s"
                                )
                                % dependency,
                                "course1": dependency.course1.id,
                                "course2": dependency.course2.id,
                                "type": "ConsiderDependencies",
                            }
                        )
                else:
                    jsondict["status"] = _("KO")
                    ok_so_far = False
                    jsondict["messages"].append(
                        {
                            "str": gettext(
                                f"There is no available slots for the first or the second course : %s"
                            )
                            % dependency,
                            "course1": dependency.course1.id,
                            "course2": dependency.course2.id,
                            "type": "ConsiderDependencies",
                        }
                    )

                if ok_so_far:
                    if dependency.successive:
                        if not find_successive_slots(
                            course1_slots,
                            course2_slots,
                            dependency.course1.duration,
                            dependency.course2.duration,
                        ):
                            jsondict["status"] = _("KO")
                            ok_so_far = False
                            jsondict["messages"].append(
                                {
                                    "str": gettext(
                                        f"There is no available successive slots for those courses: %s"
                                    )
                                    % dependency,
                                    "course1": dependency.course1.id,
                                    "course2": dependency.course2.id,
                                    "type": "ConsiderDependencies",
                                }
                            )
                    if dependency.day_gap != 0:
                        if not find_day_gap_slots(
                            course1_slots, course2_slots, dependency.day_gap
                        ):
                            jsondict["status"] = _("KO")
                            ok_so_far = False
                            jsondict["messages"].append(
                                {
                                    "str": gettext(
                                        "There is no available slots for the second "
                                        "course after a %(day_gap)s day gap: %(dependency)s"
                                    )
                                    % {
                                        "day_gap": dependency.day_gap,
                                        "dependency": dependency,
                                    },
                                    "course1": dependency.course1.id,
                                    "course2": dependency.course2.id,
                                    "type": "ConsiderDependencies",
                                }
                            )
            else:
                jsondict["status"] = _("KO")
                ok_so_far = False
                jsondict["messages"].append(
                    {
                        "str": gettext(
                            "One of the courses has no eligible tutor to lecture it: %s"
                        )
                        % dependency,
                        "course1": dependency.course1.id,
                        "course2": dependency.course2.id,
                        "type": "ConsiderDependencies",
                    }
                )
        return jsondict

    def considered_dependecies(self, period=None):
        """Returns the dependencies that have to be considered"""
        result = Dependency.objects.filter(
            course1__type__department=self.department,
            course2__type__department=self.department,
        )
        if period:
            result = result.filter(course1__period=period, course2__period=period)
        if self.train_progs.exists():
            result = result.filter(
                course1__module__train_prog__in=self.train_progs.all(),
                course2__module__train_prog__in=self.train_progs.all(),
            )
        if self.modules.exists():
            result = result.filter(
                course1__module__in=self.modules.all(),
                course2__module__in=self.modules.all(),
            )
        if self.periods.exists():
            result = result.filter(
                course1__period__in=self.periods.all(),
                course2__period__in=self.periods.all(),
            )
        return result

    def one_line_description(self):
        text = f"Prend en compte les précédences enregistrées en base."
        if self.train_progs.exists():
            text += " des promos " + ", ".join(
                [train_prog.abbrev for train_prog in self.train_progs.all()]
            )
        if self.modules.exists():
            text += " pour les modules " + ", ".join(
                [module.abbrev for module in self.modules.all()]
            )
        return text

    def enrich_ttmodel(self, ttmodel, period, ponderation=10):
        if self.train_progs.exists():
            train_progs = set(
                tp for tp in self.train_progs.all() if tp in ttmodel.train_prog
            )
        else:
            train_progs = set(ttmodel.train_prog)
        considered_modules = set(ttmodel.data.modules)
        if self.modules.exists():
            considered_modules &= set(self.modules.all())

        for p in ttmodel.data.dependencies:
            c1 = p.course1
            c2 = p.course2
            if (
                c1.module not in considered_modules
                and c2.module not in considered_modules
            ) or (
                c1.module.train_prog not in train_progs
                and c2.module.train_prog not in train_progs
            ):
                continue
            if c1 == c2:
                ttmodel.add_warning(
                    None, "Warning: %s is declared depend on itself" % c1
                )
                continue
            for sl1 in ttmodel.data.compatible_slots[c1]:
                if not self.weight:
                    ttmodel.add_constraint(
                        1000000 * ttmodel.scheduled[(sl1, c1)]
                        + ttmodel.sum(
                            ttmodel.scheduled[(sl2, c2)]
                            for sl2 in ttmodel.data.compatible_slots[c2]
                            if not sl2.is_after(sl1)
                            or (p.day_gap > 0 and (sl2.day - sl1.day).days < p.day_gap)
                            or (p.successive and not sl2.is_successor_of(sl1))
                        ),
                        "<=",
                        1000000,
                        DependencyConstraint(c1, c2, sl1),
                    )
                else:
                    for sl2 in ttmodel.data.compatible_slots[c2]:
                        if (
                            not sl2.is_after(sl1)
                            or (p.day_gap > 0 and (sl2.day - sl1.day).days < p.day_gap)
                            or (p.successive and not sl2.is_successor_of(sl1))
                        ):
                            conj_var = ttmodel.add_conjunct(
                                ttmodel.scheduled[(sl1, c1)],
                                ttmodel.scheduled[(sl2, c2)],
                            )
                            ttmodel.add_to_generic_cost(
                                conj_var * self.local_weight() * ponderation
                            )

    def is_satisfied_for(self, period, version):
        unrespected_dependencies = []
        for dep in self.considered_dependecies(period):
            if (
                dep.course1.scheduledcourse_set.filter(version=version).exists()
                and dep.course2.scheduledcourse_set.filter(version=version).exists()
            ):
                sched_course1 = dep.course1.scheduledcourse_set.get(version=version)
                sched_course2 = dep.course2.scheduledcourse_set.get(version=version)
                if sched_course2.start_time <= sched_course1.start_time:
                    unrespected_dependencies.append(dep)
                elif dep.day_gap > 0:
                    if (
                        sched_course2.start_time.date()
                        - sched_course1.start_time.date()
                    ).days < dep.day_gap:
                        unrespected_dependencies.append(dep)
                elif dep.successive:
                    if sched_course2.start_time > sched_course1.end_time + slot_pause:
                        unrespected_dependencies.append(dep)
        assert (
            not unrespected_dependencies
        ), f"Following dependencies do not respect global dependency :{unrespected_dependencies}"


class ConsiderPivots(TimetableConstraint):
    """
    Transform the constraints of pivots saved on the DB in model constraints:
    -include non same-day constraint
    If there is a weight, it's a preference, else it's a constraint...
    """

    train_progs = models.ManyToManyField("base.TrainingProgramme", blank=True)
    modules = models.ManyToManyField("base.Module", blank=True)

    class Meta:
        verbose_name = _("Consider pivots")
        verbose_name_plural = verbose_name

    def one_line_description(self):
        text = f"Prend en compte les pivots enregistrées en base."
        if self.train_progs.exists():
            text += " des promos " + ", ".join(
                [train_prog.abbrev for train_prog in self.train_progs.all()]
            )
        if self.modules.exists():
            text += " pour les modules " + ", ".join(
                [module.abbrev for module in self.modules.all()]
            )
        return text

    def enrich_ttmodel(self, ttmodel, period, ponderation=10):
        if self.train_progs.exists():
            train_progs = set(
                tp for tp in self.train_progs.all() if tp in ttmodel.train_prog
            )
        else:
            train_progs = set(ttmodel.train_prog)
        considered_modules = set(ttmodel.data.modules)
        if self.modules.exists():
            considered_modules &= set(self.modules.all())

        for p in ttmodel.data.pivots:
            pivot = p.pivot_course
            other = p.other_courses.all()
            other_length = other.count()
            if (
                pivot.module not in considered_modules
                and all(o.module not in considered_modules for o in other)
            ) or (
                pivot.module.train_prog not in train_progs
                and all(o.module.train_prog not in train_progs for o in other)
            ):
                continue
            if pivot in other:
                ttmodel.add_warning(
                    None, f"Warning: {pivot} is declared pivoting around itself"
                )
                continue
            for sl1 in ttmodel.data.compatible_slots[pivot]:
                all_after = ttmodel.add_floor(
                    ttmodel.sum(
                        ttmodel.scheduled[(sl2, o)]
                        for o in other
                        for sl2 in ttmodel.data.compatible_slots[o]
                        if (not p.ND and not sl2.is_after(sl1))
                        or (p.ND and (sl1.has_previous_day_than(sl2)))
                    ),
                    other_length,
                    2 * other_length,
                )
                all_before = ttmodel.add_floor(
                    ttmodel.sum(
                        ttmodel.scheduled[(sl2, o)]
                        for o in other
                        for sl2 in ttmodel.data.compatible_slots[o]
                        if (not p.ND and not sl1.is_after(sl2))
                        or (p.ND and (sl2.has_previous_day_than(sl1)))
                    ),
                    other_length,
                    2 * other_length,
                )
                if not self.weight:
                    ttmodel.add_constraint(
                        ttmodel.scheduled[(sl1, pivot)] - all_after - all_before,
                        "<=",
                        0,
                        Constraint(constraint_type=ConstraintType.PIVOT, slots=sl1),
                    )
                else:
                    undesired_situation = ttmodel.add_floor(
                        10 * ttmodel.scheduled[(sl1, pivot)] - all_after - all_before,
                        10,
                        20,
                    )

                    ttmodel.add_to_generic_cost(
                        undesired_situation * self.local_weight() * ponderation
                    )


# Ex TimetableConstraints that have to be re-written.....


class AvoidBothTimesSameDay(TimetableConstraint):
    """
    Avoid the use of two slots
    Idéalement, on pourrait paramétrer slot1, et slot2 à partir de slot1... Genre slot1
    c'est 8h n'importe quel jour, et slot2 14h le même jour...
    """

    train_progs = models.ManyToManyField("base.TrainingProgramme", blank=True)
    time1 = models.TimeField()
    time2 = models.TimeField()
    weekdays = ArrayField(
        models.CharField(max_length=2, choices=Day.CHOICES), blank=True, null=True
    )
    groups = models.ManyToManyField("base.StructuralGroup", blank=True)

    class Meta:
        verbose_name = _("Avoid using both times on same day")
        verbose_name_plural = verbose_name

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(["groups", "train_progs"])
        return attributes

    def enrich_ttmodel(self, ttmodel, period, ponderation=1):
        considered_groups = self.considered_basic_groups(ttmodel)
        days = days_filter(ttmodel.data.days, period=period)
        slots1 = set(
            [
                slot
                for slot in ttmodel.data.courses_slots
                if slot.start_time.time() <= self.time1 < slot.end_time.time()
            ]
        )
        slots2 = set(
            [
                slot
                for slot in ttmodel.data.courses_slots
                if slot.start_time.time() <= self.time2 < slot.end_time.time()
            ]
        )
        if self.weekdays:
            days = days_filter(days, weekday_in=self.weekdays)
        for day in days:
            day_slots1 = slots_filter(slots1, day=day)
            day_slots2 = slots_filter(slots2, day=day)
            for group in considered_groups:
                considered_courses = self.get_courses_queryset_by_parameters(
                    period, ttmodel, group=group
                )
                sum1 = ttmodel.sum(
                    ttmodel.scheduled[sl, c]
                    for c in considered_courses
                    for sl in day_slots1 & ttmodel.data.compatible_slots[c]
                )
                sum2 = ttmodel.sum(
                    ttmodel.scheduled[sl, c]
                    for c in considered_courses
                    for sl in day_slots2 & ttmodel.data.compatible_slots[c]
                )
                BS1 = ttmodel.add_floor(sum1, 1, 100000)
                BS2 = ttmodel.add_floor(sum2, 1, 100000)
                both = ttmodel.add_conjunct(BS1, BS2)
                if self.weight is None:
                    ttmodel.add_constraint(
                        both,
                        "==",
                        0,
                        Constraint(
                            constraint_type=ConstraintType.AVOID_BOTH_TIME_SAME_DAY,
                            groups=group,
                            days=day,
                            periods=period,
                        ),
                    )
                else:
                    ttmodel.add_to_group_cost(
                        group, self.local_weight() * ponderation * both, period=period
                    )

    def one_line_description(self):
        text = f"Pas à la fois à {self.time1} et à {self.time2}"
        if self.train_progs.exists():
            text += " des promos " + ", ".join(
                [train_prog.abbrev for train_prog in self.train_progs.all()]
            )
        else:
            text += " de toutes les promos."
        return text


class LimitUndesiredSlotsPerDayPeriod(TimetableConstraint):
    """
    Allow to limit the number of undesired slots per period
    start_time and end_time are in minuts from 0:00 AM
    """

    tutors = models.ManyToManyField(
        "people.Tutor", blank=True, verbose_name=_("Tutors")
    )
    slot_start_time = models.TimeField()
    slot_end_time = models.TimeField()
    max_number = models.PositiveSmallIntegerField(validators=[MaxValueValidator(7)])

    class Meta:
        verbose_name = _("Limit undesired slots per period")
        verbose_name_plural = verbose_name

    def enrich_ttmodel(self, ttmodel, period, ponderation=1):
        tutor_to_be_considered = considered_tutors(self, ttmodel)
        days = days_filter(ttmodel.data.days, period=period)
        undesired_slots = [
            Slot(
                dt.datetime.combine(day, self.slot_start_time),
                dt.datetime.combine(day, self.slot_end_time),
            )
            for day in days
        ]
        for tutor in tutor_to_be_considered:
            considered_courses = self.get_courses_queryset_by_parameters(
                period, ttmodel, tutor=tutor
            )
            expr = ttmodel.lin_expr()
            for undesired_slot in undesired_slots:
                expr += ttmodel.add_floor(
                    ttmodel.sum(
                        ttmodel.assigned[(sl, c, tutor)]
                        for c in considered_courses
                        for sl in slots_filter(
                            ttmodel.data.courses_slots, simultaneous_to=undesired_slot
                        )
                        & ttmodel.data.compatible_slots[c]
                    ),
                    1,
                    len(considered_courses),
                )
            if self.weight is None:
                ttmodel.add_constraint(
                    expr,
                    "<=",
                    self.max_number,
                    Constraint(
                        constraint_type=ConstraintType.Undesired_slots_limit,
                        instructors=tutor,
                    ),
                )
            else:
                for i in range(self.max_number + 1, len(days) + 1):
                    cost = self.local_weight() * ponderation
                    undesired_situation = ttmodel.add_floor(expr, i, len(days))
                    ttmodel.add_to_inst_cost(tutor, cost * undesired_situation, period)
                    cost *= 2

    def one_line_description(self):
        text = ""
        if self.tutors.exists():
            text += ", ".join([tutor.username for tutor in self.tutors.all()])
        else:
            text += "Les profs"
        text += (
            f" n'ont pas cours plus de {self.max_number} jours par semaine "
            f"entre {self.slot_start_time} et {self.slot_end_time}"
        )
        return text


class LimitSimultaneousCoursesNumber(TimetableConstraint):
    """
    Limit the number of simultaneous courses inside a set of courses, and/or selecting a specific course type
    and/or a set of considered modules
    """

    limit = models.PositiveSmallIntegerField()
    course_type = models.ForeignKey(
        "base.CourseType", on_delete=models.CASCADE, null=True, blank=True
    )
    modules = models.ManyToManyField(
        "base.Module", blank=True, related_name="limit_simultaneous"
    )

    class Meta:
        verbose_name = _("Limit simultaneous courses number")
        verbose_name_plural = verbose_name

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(["course_type", "modules"])
        return attributes

    def enrich_ttmodel(self, ttmodel, period, ponderation=1):
        relevant_courses = ttmodel.data.courses
        if self.course_type is not None:
            relevant_courses = relevant_courses.filter(type=self.course_type)
        if self.modules.exists():
            relevant_courses = relevant_courses.filter(module__in=self.modules.all())
        nb_courses = relevant_courses.count()
        if nb_courses <= self.limit:
            return
        relevant_sum = ttmodel.lin_expr()
        if self.weight is None:
            for a_sl in ttmodel.data.availability_slots:
                more_than_limit = ttmodel.add_floor(
                    ttmodel.sum(
                        ttmodel.scheduled[sl, c]
                        for c in relevant_courses
                        for sl in slots_filter(
                            ttmodel.data.compatible_slots[c], simultaneous_to=a_sl
                        )
                    ),
                    self.limit + 1,
                    nb_courses,
                )
                relevant_sum += more_than_limit
            ttmodel.add_constraint(
                relevant_sum,
                "==",
                0,
                Constraint(
                    constraint_type=ConstraintType.LimitSimultaneousCoursesNumber,
                    periods=period,
                ),
            )
        else:
            for bound in range(self.limit, nb_courses + 1):
                relevant_sum *= 2
                for a_sl in ttmodel.data.availability_slots:
                    more_than_limit = ttmodel.add_floor(
                        ttmodel.sum(
                            ttmodel.scheduled[sl, c]
                            for c in relevant_courses
                            for sl in slots_filter(
                                ttmodel.data.compatible_slots[c], simultaneous_to=a_sl
                            )
                        ),
                        bound + 1,
                        nb_courses,
                    )
                    relevant_sum += more_than_limit
            ttmodel.add_to_generic_cost(
                self.local_weight() * ponderation * relevant_sum
            )

    def get_viewmodel(self):
        view_model = super().get_viewmodel()
        details = view_model["details"]

        details.update(
            {
                "limit": self.limit,
                "course_type": self.course_type.name if self.course_type else None,
                "modules": ", ".join([m.abbrev for m in self.modules.all()]),
            }
        )

        return view_model

    def one_line_description(self):
        text = f"Parmi les cours"
        if self.course_type:
            text += f" de type {self.course_type.name}"
        if self.modules.exists():
            text += f" des modules {', '.join([m.abbrev for m in self.modules.all()])}"
        text += f" au maximum {self.limit} peuvent être simultanés."
        return text
