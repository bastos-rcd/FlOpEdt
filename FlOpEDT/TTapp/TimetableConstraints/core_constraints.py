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
# <http://www.gnu.org/licenses/>
# you develop activities involving the FlOpEDT/FlOpScheduler software
# without disclosing the source code of your own applications.


import datetime as dt

from django.db import models
from django.db.models import Q
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

import TTapp.global_pre_analysis.partition_with_constraints as partition_bis
from base.models import (
    Course,
    CourseStartTimeConstraint,
    CourseType,
    Holiday,
    Module,
    ModuleTutorRepartition,
)
from base.models.availability import period_actual_availabilities
from base.partition import Partition
from base.timing import TimeInterval
from core.decorators import timer
from people.models import Tutor
from TTapp.ilp_constraints.constraint import Constraint
from TTapp.ilp_constraints.constraint_type import ConstraintType
from TTapp.ilp_constraints.constraints.course_constraint import CourseConstraint
from TTapp.ilp_constraints.constraints.insctructor_constraint import (
    InstructorConstraint,
)
from TTapp.ilp_constraints.constraints.simul_slot_group_constraint import (
    SimulSlotGroupConstraint,
)
from TTapp.ilp_constraints.constraints.slot_instructor_constraint import (
    SlotInstructorConstraint,
)
from TTapp.slots import slots_filter
from TTapp.TimetableConstraints.no_course_constraints import NoTutorCourseOnWeekDay
from TTapp.TimetableConstraints.timetable_constraint import TimetableConstraint


class NoSimultaneousGroupCourses(TimetableConstraint):
    """
    Only one course for each considered group on simultaneous slots
    """

    train_progs = models.ManyToManyField("base.TrainingProgramme", blank=True)
    groups = models.ManyToManyField("base.StructuralGroup", blank=True)

    class Meta:
        verbose_name = _("No simultaneous courses for groups")
        verbose_name_plural = verbose_name

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(["train_progs", "groups"])
        return attributes

    @timer
    def pre_analyse(self, period):
        """Pre analysis of the Constraint
        Compare the available time of the period to the minimum
        required in any cases (the time of all courses + the time needed
        for the longest parallel group)
        then to the probable mimimum required (the time of all courses
        + the time of all parallel groups that are maximum of their graph color) and then
        checks if there is enough available slots for each course type in the period.

        Parameter:
            period (SchedulingPeriod): the period we want to analyse the data from

        Returns:
            JsonResponse: with status 'KO' or 'OK' and a list of messages explaining the problem
        """
        jsondict = {
            "status": _("OK"),
            "messages": [],
            "period": {"id": period.id, "name": period.name},
        }

        considered_basic_groups = self.considered_basic_groups()
        no_user_pref = not ConsiderTutorsUnavailability.objects.filter(
            periods=period
        ).exists()
        for bg in considered_basic_groups:
            # Retrieving information about general time settings
            # and creating the partition with information about other constraints
            group_partition = partition_bis.create_group_partition_from_constraints(
                period=period,
                department=bg.type.department,
                group=bg,
                available=no_user_pref,
            )

            ### Coloration ###
            tuple_graph = coloration_ordered(bg)
            ### Coloration ###

            # We are looking for the maximum courses' time of transversal groups
            max_courses_time_transversal = 0

            if tuple_graph:
                graph, color_max = tuple_graph
                for transversal_group in graph:
                    time_courses = transversal_group.time_of_courses(period)
                    max_courses_time_transversal = max(
                        max_courses_time_transversal, time_courses
                    )

            # We are looking for the minimum transversal_groups we need to consider
            transversal_conflict_groups = set()
            if tuple_graph:
                for i in range(1, color_max + 1):
                    groups = []
                    for summit, graph_dict in graph.items():
                        if graph_dict["color"] == i:
                            groups.append(summit)

                    group_to_consider = groups[0]
                    time_group_courses = groups[0].time_of_courses(period)
                    for gp in groups:
                        if gp.time_of_courses(period) > time_group_courses:
                            group_to_consider = gp
                            time_group_courses = gp.time_of_courses(period)
                    transversal_conflict_groups.add(group_to_consider)

            # Set of courses for the group and all its structural ancestors
            considered_courses = set(
                c
                for c in Course.objects.filter(
                    period=period, groups__in=bg.and_ancestors()
                )
            )

            # Mimimum time needed in any cases
            min_course_time_needed = (
                sum(c.duration for c in considered_courses)
                + max_courses_time_transversal
            )

            if min_course_time_needed > group_partition.not_forbidden_duration:
                jsondict["status"] = _("KO")
                jsondict["messages"].append(
                    {
                        "str": gettext(
                            "Group %(group_name)s has %(not_forbidden_duration)s "
                            "available time but requires minimum %(min_course_time_needed)s."
                        )
                        % {
                            "group_name": bg.name,
                            "not_forbidden_duration": group_partition.not_forbidden_duration,
                            "min_course_time_needed": min_course_time_needed,
                        },
                        "group": bg.id,
                        "type": "NoSimultaneousGroupCourses",
                    }
                )

            else:
                # If they exists we add the transversal courses to the considered_courses
                if transversal_conflict_groups:
                    considered_courses = considered_courses | set(
                        c
                        for c in Course.objects.filter(
                            period=period, groups__in=transversal_conflict_groups
                        )
                    )

                # If we are below that amount of time we probably cannot do it.
                course_time_needed = sum(c.duration for c in considered_courses)

                if course_time_needed > group_partition.not_forbidden_duration:
                    jsondict["status"] = _("KO")
                    jsondict["messages"].append(
                        {
                            "str": gettext(
                                "Group %(group_name)s has %(not_forbidden_duration)s "
                                "available time but probably requires "
                                "minimum %(min_course_time_needed)s."
                            )
                            % {
                                "group_name": bg.name,
                                "not_forbidden_duration": group_partition.not_forbidden_duration,
                                "min_course_time_needed": min_course_time_needed,
                            },
                            "group": bg.id,
                            "type": "NoSimultaneousGroupCourses",
                        }
                    )

                else:
                    # We are checking if we have enough slots for the number of courses

                    # We gather the courses by type

                    course_dict = {}
                    for c in considered_courses:
                        if c.duration in course_dict:
                            course_dict[c.duration] += 1
                        else:
                            course_dict[c.duration] = 1

                    all_start_times = []
                    all_nb_courses = 0
                    min_duration = dt.timedelta(minutes=1440)

                    for course_duration, nb_courses in course_dict.items():
                        # We compute the total number of courses, all the different
                        # start times and the minimum duration of course
                        all_nb_courses += nb_courses
                        start_times = CourseStartTimeConstraint.objects.get(
                            duration=course_duration, department=self.department
                        ).allowed_start_times
                        min_duration = min(course_duration, min_duration)

                        for st in start_times:
                            if st not in all_start_times:
                                all_start_times.append(st)

                        # We look if there is enough slot for each course_type

                        slots_nb = group_partition.nb_slots_not_forbidden_of_duration_beginning_at(
                            course_duration, start_times
                        )

                        if slots_nb < nb_courses:
                            jsondict["status"] = _("KO")
                            jsondict["messages"].append(
                                {
                                    "str": gettext(
                                        "Group %(group_name)s has %(allowed_slots_nb)s "
                                        "slots available of %(duration)s minutes "
                                        "and requires %(nb_courses)s."
                                    )
                                    % {
                                        "group_name": bg.name,
                                        "allowed_slots_nb": slots_nb,
                                        "duration": course_duration,
                                        "nb_courses": nb_courses,
                                    },
                                    "group": bg.id,
                                    "type": "NoSimultaneousGroupCourses",
                                }
                            )
                            return jsondict

                    # To try to avoid conflict we are looking if there are
                    # enough slots for all courses at all start times possible
                    # for the minimum duration of all courses. Not always find
                    # an infeasibility but can quickly find conflict in some case.

                    all_allowed_slots_nb = (
                        group_partition.nb_slots_not_forbidden_of_duration_beginning_at(
                            min_duration, all_start_times
                        )
                    )

                    if all_allowed_slots_nb < all_nb_courses:
                        jsondict["status"] = _("KO")
                        jsondict["messages"].append(
                            {
                                "str": _(
                                    "Group %(group_name)s has a total "
                                    "of %(all_allowed_slots_nb)s slots available "
                                    "of minimum %(min_duration)s minutes "
                                    "and requires %(all_nb_courses)s."
                                )
                                % {
                                    "group_name": bg.name,
                                    "all_allowed_slots_nb": all_allowed_slots_nb,
                                    "min_duration": min_duration,
                                    "all_nb_courses": all_nb_courses,
                                },
                                "group": bg.id,
                                "type": "NoSimultaneousGroupCourses",
                            }
                        )

        return jsondict

    def enrich_ttmodel(self, ttmodel, period, ponderation=1):
        relevant_slots = slots_filter(ttmodel.data.availability_slots, period=period)
        relevant_basic_groups = self.considered_basic_groups(ttmodel)
        # Count the number of transversal groups
        if ttmodel.data.transversal_groups.exists():
            n_tg = ttmodel.data.transversal_groups.count()
        else:
            n_tg = 1
        for sl in relevant_slots:
            for bg in relevant_basic_groups:
                relevant_sum = n_tg * ttmodel.sum(
                    ttmodel.scheduled[(sl2, c2)]
                    for sl2 in slots_filter(
                        ttmodel.data.courses_slots, simultaneous_to=sl
                    )
                    for c2 in ttmodel.data.courses_for_basic_group[bg]
                    & ttmodel.data.compatible_courses[sl2]
                ) + ttmodel.sum(
                    ttmodel.scheduled[(sl2, c2)]
                    for tg in ttmodel.data.transversal_groups_of[bg]
                    for sl2 in slots_filter(
                        ttmodel.data.courses_slots, simultaneous_to=sl
                    )
                    for c2 in ttmodel.data.courses_for_group[tg]
                    & ttmodel.data.compatible_courses[sl2]
                )
                if self.weight is None:
                    ttmodel.add_constraint(
                        relevant_sum, "<=", n_tg, SimulSlotGroupConstraint(sl, bg)
                    )
                else:
                    two_courses = ttmodel.add_floor(
                        relevant_sum, n_tg + 1, n_tg * len(relevant_slots)
                    )
                    ttmodel.add_to_group_cost(
                        bg, self.local_weight() * ponderation * two_courses, period
                    )

            for tg in ttmodel.data.transversal_groups:
                # The "+1" is for the case where all transversal groups are parallel
                not_parallel_nb_bound = (
                    len(ttmodel.data.not_parallel_transversal_groups[tg]) + 1
                )
                relevant_sum_for_tg = not_parallel_nb_bound * ttmodel.sum(
                    ttmodel.scheduled[(sl2, c2)]
                    for sl2 in slots_filter(
                        ttmodel.data.courses_slots, simultaneous_to=sl
                    )
                    for c2 in ttmodel.data.courses_for_group[tg]
                    & ttmodel.data.compatible_courses[sl2]
                ) + ttmodel.sum(
                    ttmodel.scheduled[(sl2, c2)]
                    for tg2 in ttmodel.data.not_parallel_transversal_groups[tg]
                    for sl2 in slots_filter(
                        ttmodel.data.courses_slots, simultaneous_to=sl
                    )
                    for c2 in ttmodel.data.courses_for_group[tg2]
                    & ttmodel.data.compatible_courses[sl2]
                )
                if self.weight is None:
                    ttmodel.add_constraint(
                        relevant_sum_for_tg,
                        "<=",
                        not_parallel_nb_bound,
                        SimulSlotGroupConstraint(sl, tg),
                    )
                else:
                    two_courses = ttmodel.add_floor(
                        relevant_sum_for_tg, 2, len(relevant_slots)
                    )
                    ttmodel.add_to_global_cost(
                        self.local_weight() * ponderation * two_courses, period
                    )

    def one_line_description(self):
        text = "Les cours "
        if self.groups.exists():
            text += " des groupes " + ", ".join(
                [group.name for group in self.groups.all()]
            )
        else:
            text += " de chaque groupe"
        if self.train_progs.exists():
            text += " de " + ", ".join(
                [train_prog.abbrev for train_prog in self.train_progs.all()]
            )
        text += " ne peuvent pas être simultanés"
        return text

    def __str__(self):
        return "No simultaneous courses for one group"

    def is_satisfied_for(self, period, version):
        relevant_scheduled_courses = self.period_version_scheduled_courses_queryset(
            period, version
        )
        relevant_basic_groups = self.considered_basic_groups()
        problematic_groups = []
        for bg in relevant_basic_groups:
            bg_scheduled_courses = relevant_scheduled_courses.filter(
                course__groups__in=bg.and_ancestors()
            )
            for sched_course in bg_scheduled_courses:
                for sched_course2 in bg_scheduled_courses.filter(
                    id__gt=sched_course.id
                ):
                    if sched_course.is_simultaneous_to(sched_course2):
                        problematic_groups.append(bg)
        assert not problematic_groups, (
            f"{self} is not satisfied for period {period}, "
            f"version {version} and following groups : {problematic_groups}"
        )


class ScheduleAllCourses(TimetableConstraint):
    """
    The considered courses are scheduled, and only once
    """

    train_progs = models.ManyToManyField("base.TrainingProgramme", blank=True)
    modules = models.ManyToManyField("base.Module", blank=True)
    groups = models.ManyToManyField("base.StructuralGroup", blank=True)
    tutors = models.ManyToManyField("people.Tutor", blank=True)
    course_types = models.ManyToManyField("base.CourseType", blank=True)

    class Meta:
        verbose_name = _("Schedule once all considered courses")
        verbose_name_plural = verbose_name

    def is_satisfied_for(self, period, version):
        unscheduled = []
        scheduled_more_than_once = []
        considered_scheduled_courses = self.period_version_scheduled_courses_queryset(
            period, version
        )
        for c in self.considered_courses(period):
            if considered_scheduled_courses.filter(course=c).count() == 0:
                unscheduled.append(c)
            elif considered_scheduled_courses.filter(course=c).count() > 1:
                scheduled_more_than_once.append(c)
        not_asserted_text = (
            f"{self} is not satisfied for period {period} and version {version} : "
        )
        assert not unscheduled and not scheduled_more_than_once, (
            not_asserted_text + f"not scheduled : {unscheduled}, "
            f"scheduled more than once : {scheduled_more_than_once}"
        )

    def enrich_ttmodel(self, ttmodel, period, ponderation=100):
        max_slots_nb = len(ttmodel.data.courses_slots)
        for c in self.considered_courses(period, ttmodel):
            relevant_sum = ttmodel.sum(
                [ttmodel.scheduled[(sl, c)] for sl in ttmodel.data.compatible_slots[c]]
            )
            if self.weight is None:
                ttmodel.add_constraint(relevant_sum, "==", 1, CourseConstraint(c))
            else:
                not_scheduled = ttmodel.add_floor(relevant_sum, 1, max_slots_nb)
                ttmodel.add_to_generic_cost(
                    (ttmodel.one_var - not_scheduled)
                    * self.local_weight()
                    * ponderation,
                    period,
                )

    def one_line_description(self):
        text = "Planifie tous les cours "
        if self.groups.exists():
            text += " des groupes " + ", ".join(
                [group.name for group in self.groups.all()]
            )
        if self.train_progs.exists():
            text += " de " + ", ".join(
                [train_prog.abbrev for train_prog in self.train_progs.all()]
            )
        if self.modules.exists():
            text += " de : " + ", ".join([str(module) for module in self.modules.all()])
        if self.course_types.exists():
            text += " de type" + ", ".join([t.name for t in self.course_types.all()])
        if self.tutors.exists():
            text += " de " + ", ".join([tutor.username for tutor in self.tutors.all()])
        return text


class AssignAllCourses(TimetableConstraint):
    """
    The considered courses are assigned to a tutor
    If pre_assigned_only, it does assign a tutor only to courses that already have one
    """

    train_progs = models.ManyToManyField("base.TrainingProgramme", blank=True)
    modules = models.ManyToManyField("base.Module", blank=True)
    groups = models.ManyToManyField("base.StructuralGroup", blank=True)
    course_types = models.ManyToManyField("base.CourseType", blank=True)
    pre_assigned_only = models.BooleanField(
        default=False, verbose_name=_("Pre-assigned courses only")
    )

    class Meta:
        verbose_name = _("Each course is assigned to one tutor (max)")
        verbose_name_plural = verbose_name

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(["train_progs", "modules", "groups", "course_types"])
        return attributes

    def no_tutor_courses(self, period, ttmodel=None):
        return self.tutors_courses_and_no_tutor_courses(period, ttmodel)[1]

    def tutors_courses_and_no_tutor_courses(self, period, ttmodel=None):
        considered_courses = self.considered_courses(period, ttmodel)
        if self.pre_assigned_only:
            no_tutor_courses = set(c for c in considered_courses if c.tutor is None)
            tutor_courses = set(c for c in considered_courses if c.tutor is not None)
        else:
            tutor_courses = considered_courses
            no_tutor_courses = set()

        return tutor_courses, no_tutor_courses

    def enrich_ttmodel(self, ttmodel, period, ponderation=100):
        tutor_courses, no_tutor_courses = self.tutors_courses_and_no_tutor_courses(
            period, ttmodel
        )
        for c in tutor_courses:
            for sl in ttmodel.data.compatible_slots[c]:
                relevant_sum = (
                    ttmodel.sum(
                        ttmodel.assigned[(sl, c, i)]
                        for i in ttmodel.data.possible_tutors[c]
                    )
                    - ttmodel.scheduled[sl, c]
                )
                if self.weight is None:
                    ttmodel.add_constraint(
                        relevant_sum,
                        "==",
                        0,
                        InstructorConstraint(
                            constraint_type=ConstraintType.COURS_DOIT_AVOIR_PROFESSEUR,
                            slot=sl,
                            course=c,
                        ),
                    )
                else:
                    ttmodel.add_constraint(
                        relevant_sum,
                        "<=",
                        0,
                        InstructorConstraint(
                            constraint_type=ConstraintType.COURS_DOIT_AVOIR_PROFESSEUR,
                            slot=sl,
                            course=c,
                        ),
                    )
                    assigned = ttmodel.add_floor(relevant_sum, 0, 1000)
                    ttmodel.add_to_generic_cost(
                        (1 - assigned) * self.local_weight() * ponderation, period
                    )
        if self.pre_assigned_only:
            possible_useless_assignations_sum = ttmodel.sum(
                ttmodel.assigned[(sl, c, i)]
                for c in no_tutor_courses
                for sl in ttmodel.data.compatible_slots[c]
                for i in ttmodel.data.possible_tutors[c]
            )
            ttmodel.add_constraint(
                possible_useless_assignations_sum,
                "==",
                0,
                Constraint(constraint_type=ConstraintType.PRE_ASSIGNED_TUTORS_ONLY),
            )

    def is_satisfied_for(self, period, version):
        tutor_courses, _ = self.tutors_courses_and_no_tutor_courses(period)
        considered_scheduled_courses = self.period_version_scheduled_courses_queryset(
            period, version
        )
        unassigned_scheduled_courses = considered_scheduled_courses.filter(
            course__in=tutor_courses, tutor__isnull=True
        )
        assert not unassigned_scheduled_courses.exists(), (
            f"{self} is not satisfied for period {period} and version {version}. "
            "The following courses are not assigned to a tutor : {unassigned_scheduled_courses}"
        )

    def one_line_description(self):
        text = "Assigne tous les cours "
        if self.groups.exists():
            text += " des groupes " + ", ".join(
                [group.name for group in self.groups.all()]
            )
        if self.train_progs.exists():
            text += " de " + ", ".join(
                [train_prog.abbrev for train_prog in self.train_progs.all()]
            )
        if self.modules.exists():
            text += " de : " + ", ".join([str(module) for module in self.modules.all()])
        if self.course_types.exists():
            text += " de type" + ", ".join([t.name for t in self.course_types.all()])
        text += " à un prof."
        return text

    def __str__(self):
        return "Each course is assigned to one tutor (max)"


class ConsiderModuleTutorRepartitions(TimetableConstraint):
    """
    The courses are assigned to tutors according to their ModuleTutorRepartition
    Even if weight is not None, all considered courses are assigned to some tutor
    """

    modules = models.ManyToManyField("base.Module", blank=True)
    course_types = models.ManyToManyField("base.CourseType", blank=True)

    def one_line_description(self):
        text = "Considère les répartitions des cours "
        if self.modules.exists():
            text += " des modules " + ", ".join(
                [module.name for module in self.modules.all()]
            )
        if self.course_types.exists():
            text += " de type" + ", ".join([t.name for t in self.course_types.all()])
        text += " par prof."
        return text

    def considered_modules(self, ttmodel=None):
        if ttmodel is not None:
            considered_modules = set(ttmodel.data.modules)
        else:
            considered_modules = set(
                Module.objects.filter(train_prog__department=self.department)
            )
        if self.modules.exists():
            considered_modules &= set(self.modules.all())
        return considered_modules

    def considered_course_types(self, ttmodel=None):
        if ttmodel is not None:
            considered_course_types = set(ttmodel.data.course_types)
        else:
            considered_course_types = set(
                CourseType.objects.filter(department=self.department)
            )
        if self.course_types.exists():
            considered_course_types &= set(self.course_types.all())
        return considered_course_types

    def enrich_ttmodel(self, ttmodel, period, ponderation=1):
        for module in self.considered_modules(ttmodel):
            for course_type in self.considered_course_types(ttmodel):
                considered_mtr = ModuleTutorRepartition.objects.filter(
                    period=period, module=module, course_type=course_type
                )
                if not considered_mtr.exists():
                    continue
                max_mtr_nb = max(mtr.courses_nb for mtr in considered_mtr)
                total_mtr_course_nb = sum(mtr.courses_nb for mtr in considered_mtr)
                considered_courses = set(
                    c
                    for c in ttmodel.data.courses
                    if c.module == module
                    and c.type == course_type
                    and c.period == period
                    and c.tutor is None
                )
                for mtr in considered_mtr:
                    considered_sum = ttmodel.sum(
                        ttmodel.assigned[sl, c, mtr.tutor]
                        for c in considered_courses
                        for sl in slots_filter(
                            ttmodel.data.compatible_slots[c], period=mtr.period
                        )
                    )

                    if self.weight is None:
                        ttmodel.add_constraint(
                            considered_sum,
                            "==",
                            mtr.courses_nb,
                            Constraint(
                                constraint_type=ConstraintType.MODULE_TUTOR_REPARTITION
                            ),
                        )
                    else:
                        differences = [
                            ttmodel.add_floor(
                                considered_sum - mtr.courses_nb * ttmodel.one_var,
                                i,
                                max_mtr_nb + 2,
                            )
                            for i in range(1, max_mtr_nb + 1)
                        ]
                        for diff in differences:
                            cost = self.local_weight() * ponderation
                            ttmodel.add_to_generic_cost(cost * diff, period)
                            cost *= 2

                if self.weight is not None:
                    all_tutors = set(mtr.tutor for mtr in considered_mtr)
                    ttmodel.add_constraint(
                        ttmodel.sum(
                            ttmodel.assigned[sl, c, tutor]
                            for tutor in all_tutors
                            for c in considered_courses
                            for sl in ttmodel.data.compatible_slots[c]
                        ),
                        "==",
                        total_mtr_course_nb,
                        Constraint(
                            constraint_type=ConstraintType.MODULE_TUTOR_REPARTITION
                        ),
                    )

    def is_satisfied_for(self, period, version):
        considered_scheduled_courses = self.period_version_scheduled_courses_queryset(
            period, version
        )
        if not considered_scheduled_courses.exists():
            return
        unsatisfied_mtr = []
        for module in self.considered_modules():
            for course_type in self.considered_course_types():
                considered_mtr = ModuleTutorRepartition.objects.filter(
                    period=period, module=module, course_type=course_type
                )
                if not considered_mtr.exists():
                    continue
                total_mtr_course_nb = sum(mtr.courses_nb for mtr in considered_mtr)
                mod_and_ct_considered_scheduled_courses = (
                    considered_scheduled_courses.filter(
                        course__module=module, course__type=course_type
                    )
                )
                if (
                    mod_and_ct_considered_scheduled_courses.count()
                    != total_mtr_course_nb
                ):
                    unsatisfied_mtr.append((module, course_type))
                    continue
                for mtr in considered_mtr:
                    scheduled_courses = mod_and_ct_considered_scheduled_courses.filter(
                        tutor=mtr.tutor
                    )
                    if scheduled_courses.count() != mtr.courses_nb:
                        unsatisfied_mtr.append((module, course_type, mtr.tutor))
        assert (
            not unsatisfied_mtr
        ), f"{self} is not satisfied for period {period} and version {version}  : {unsatisfied_mtr}"


class ConsiderTutorsUnavailability(TimetableConstraint):
    tutors = models.ManyToManyField("people.Tutor", blank=True)

    class Meta:
        verbose_name = _("Consider tutors' unvailabilities")
        verbose_name_plural = verbose_name

    @timer
    def pre_analyse(self, period, spec_tutor=None):
        """Pre analysis of the Constraint
        For each tutor considered, checks if he or she has enough time available
        during the period and then
        if he or she has enough slots for each type of courses
        It takes in consideration the scheduled courses of other departments

        Parameters:
            period (SchedulingPeriod): the period we want to analyse the data from
            spec_tutor (Tutor): the tutor we want to consider.
            If None, we'll consider tutors from the constraint

        Returns:
            JsonResponse: with status 'KO' or 'OK' and a list of messages explaining the problem
        """
        jsondict = {
            "status": _("OK"),
            "messages": [],
            "period": {"id": period.id, "name": period.name},
        }
        if spec_tutor:
            considered_tutors = [spec_tutor]
        else:
            considered_tutors = self.tutors.all()

        if not considered_tutors:
            considered_tutors = Tutor.objects.filter(departments=self.department)

        for tutor in considered_tutors:
            courses = Course.objects.filter(
                Q(tutor=tutor) | Q(supp_tutors=tutor), period=period
            )
            if not courses.filter(type__department=self.department):
                continue

            tutor_partition = partition_bis.create_tutor_partition_from_constraints(
                period=period, department=self.department, tutor=tutor
            )

            if tutor_partition.available_duration < sum(c.duration for c in courses):
                message = gettext(
                    "Tutor %(tutor)s has %(available_duration)s minutes of available time."
                ) % {
                    "tutor": tutor,
                    "available_duration": int(tutor_partition.available_duration),
                }
                message += gettext(
                    " He or she has to lecture %(classes_nb)s classes "
                    "for an amount of %(duration)s minutes of courses."
                ) % {
                    "classes_nb": len(courses),
                    "duration": sum(c.duration for c in courses),
                }
                jsondict["messages"].append(
                    {
                        "str": message,
                        "tutor": tutor.id,
                        "type": "ConsiderTutorsUnavailability",
                    }
                )
                jsondict["status"] = _("KO")

            else:
                no_course_tutor = NoTutorCourseOnWeekDay.objects.filter(
                    Q(tutors=tutor) | Q(tutor_status=tutor.status) | Q(tutors=None),
                    department=self.department,
                    periods=period,
                )
                if not no_course_tutor:
                    no_course_tutor = NoTutorCourseOnWeekDay.objects.filter(
                        Q(tutors=tutor) | Q(tutor_status=tutor.status) | Q(tutors=None),
                        department=self.department,
                        periods=None,
                    )
                forbidden_days = ""
                if no_course_tutor.exists():
                    for constraint in no_course_tutor:
                        forbidden_days += (
                            constraint.weekday + "-" + constraint.periods + ", "
                        )
                        slot = constraint.get_slot_constraint(period, forbidden=True)
                        if slot:
                            tutor_partition.add_slot(
                                slot[0], "no_course_tutor", slot[1]
                            )
                    # we remove the last ','
                    forbidden_days = forbidden_days[:-2]

                holidays = Holiday.objects.filter(date__in=period.dates())
                holiday_text = ""
                if holidays.exists():
                    for h in holidays:
                        holiday_text += h.day + ", "
                        start = dt.datetime.combine(h.date, dt.time(0))
                        end = start + dt.timedelta(days=1)
                        t = TimeInterval(start, end)
                        tutor_partition.add_slot(t, "holiday", {"forbidden": True})
                    holiday_text = holiday_text[:-2]

                if tutor_partition.available_duration < sum(
                    c.duration for c in courses
                ):
                    message = gettext(
                        "Tutor %(tutor)s has %(available_duration)s minutes of available time"
                    ) % {
                        "tutor": tutor,
                        "available_duration": int(tutor_partition.available_duration),
                    }
                    if forbidden_days or holiday_text:
                        message += gettext(" (considering that")
                        if forbidden_days:
                            message += gettext(" %s is forbidden") % forbidden_days
                            if holidays:
                                message += (
                                    gettext(" and %s is holiday).") % holiday_text
                                )
                            else:
                                message += ")."
                        else:
                            message += gettext(" %s is holiday).") % holiday_text
                    else:
                        message += "."
                    message += gettext(
                        " He or she has to lecture %(classes_nb)s classes "
                        "for an amount of %(duration)s minutes of courses."
                    ) % {
                        "classes_nb": len(courses),
                        "duration": sum(c.duration for c in courses),
                    }
                    jsondict["messages"].append(
                        {
                            "str": message,
                            "tutor": tutor.id,
                            "type": "ConsiderTutorsUnavailability",
                        }
                    )
                    jsondict["status"] = _("KO")

                elif courses.exists():
                    # We build a dictionary with the courses' duration as keys
                    # and list of courses of those duration as values
                    courses_duration = {}
                    for course in courses:
                        if not course.duration in courses_duration:
                            courses_duration[course.duration] = [course]
                        else:
                            courses_duration[course.duration].append(course)

                    # For each course type we build a partition with the approriate
                    # time settings, the scheduled courses of other departments
                    # and the availabilities of the tutor and we check
                    # if the tutor has enough available time and slots.
                    for course_duration, course_list in courses_duration.items():
                        start_times = CourseStartTimeConstraint.objects.get(
                            duration=course_duration, department=self.department
                        ).allowed_start_times
                        course_partition = Partition.get_partition_of_period(
                            period, self.department, True
                        )
                        course_partition.add_scheduled_courses_to_partition(
                            period, self.department, tutor, True
                        )
                        course_partition.add_partition_data_type(
                            tutor_partition, "user_preference"
                        )
                        slots_nb = course_partition.nb_slots_available_of_duration_beginning_at(
                            course_duration, start_times
                        )
                        if course_partition.available_duration < len(
                            course_list
                        ) * course_duration or slots_nb < len(course_list):
                            message = gettext(
                                "Tutor %(tutor)s has %(slots_nb)s available "
                                "slots of %(duration)s mins "
                            ) % {
                                "tutor": tutor,
                                "slots_nb": slots_nb,
                                "duration": course_duration,
                            }
                            message += gettext(
                                "and %s courses that long to attend."
                            ) % len(course_list)
                            jsondict["messages"].append(
                                {
                                    "str": message,
                                    "tutor": tutor.id,
                                    "type": "ConsiderTutorsUnavailability",
                                }
                            )
                            jsondict["status"] = _("KO")
        return jsondict

    def enrich_ttmodel(self, ttmodel, period, ponderation=1):
        for tutor in self.considered_tutors(ttmodel):
            if tutor.username == "---":
                continue
            for sl in ttmodel.data.availability_slots:
                simultaneous_slots = slots_filter(
                    ttmodel.data.courses_slots, simultaneous_to=sl
                )
                tutor_relevant_sum = ttmodel.sum(
                    ttmodel.assigned[(sl2, c2, tutor)]
                    for sl2 in simultaneous_slots
                    for c2 in ttmodel.data.possible_courses[tutor]
                    & ttmodel.data.compatible_courses[sl2]
                )
                supp_tutors_relevant_sum = ttmodel.sum(
                    ttmodel.scheduled[(sl2, c2)]
                    for sl2 in simultaneous_slots
                    for c2 in ttmodel.data.courses_for_supp_tutors[tutor]
                    & ttmodel.data.compatible_courses[sl2]
                )
                if self.weight is None:
                    ttmodel.add_constraint(
                        tutor_relevant_sum + supp_tutors_relevant_sum,
                        "<=",
                        ttmodel.avail_instr[tutor][sl],
                        SlotInstructorConstraint(sl, tutor),
                    )
                else:
                    ttmodel.add_constraint(
                        tutor_relevant_sum + supp_tutors_relevant_sum,
                        "<=",
                        1,
                        SlotInstructorConstraint(sl, tutor),
                    )

                    tutor_undesirable_course = ttmodel.add_floor(
                        tutor_relevant_sum + supp_tutors_relevant_sum,
                        ttmodel.avail_instr[tutor][sl] + 1,
                        10000,
                    )
                    ttmodel.add_to_inst_cost(
                        tutor,
                        tutor_undesirable_course * self.local_weight() * ponderation,
                        period,
                    )

    def is_satisfied_for(self, period, version):
        considered_scheduled_courses = self.period_version_scheduled_courses_queryset(
            period, version
        )
        considered_tutors = set(sc.tutor for sc in considered_scheduled_courses)
        for sc in considered_scheduled_courses:
            considered_tutors |= set(sc.course.supp_tutors.all())
        unavailable_tutors = []
        for tutor in considered_tutors:
            tutor_courses = considered_scheduled_courses.filter(
                Q(tutor=tutor) | Q(course__supp_tutors=tutor)
            )
            user_unavailabilities = period_actual_availabilities(
                tutor, period, unavail_only=True
            )
            for sc in tutor_courses:
                if slots_filter(user_unavailabilities, simultaneous_to=sc):
                    unavailable_tutors.append(tutor)
        assert not unavailable_tutors, (
            f"{self} is not satisfied for period {period} "
            f"and version {version}. The following tutors have courses "
            f"on declared unavailabilities : {unavailable_tutors}"
        )

    def one_line_description(self):
        text = "Considère les indispos"
        if self.tutors.exists():
            text += " de " + ", ".join([tutor.username for tutor in self.tutors.all()])
        else:
            text += " de tous les profs."
        return text

    def __str__(self):
        return "Consider tutors unavailability"

    def complete_tutor_partition(self, partition, tutor, period):
        """
            Complete the partition in parameters with informations
            given by the UserAvailabilities of the given tutor for the given period.
            This method is called by functions in partition_with_constraints.py
            to initialize a partition used in pre_analyse methods.
            Warning : ConsiderTutorsUnavailability constraint must exist
            for the given period in the database to consider tutor's preferences.

        :param partition: A partition (empty or not) with informations about a tutor's availability.
        :type partition: Partition
        :param tutor: The tutor from whom the partition is about.
        :type tutor: Tutor
        :param period: The period we want to make a pre-analysis on (can be None if all).
        :type period: SchedulingPeriod
        :return: A partition with new informations about tutor's availabilities.
        :rtype: Partition

        """
        if partition.tutor_supp:
            user_unavailabilities = period_actual_availabilities(
                tutor, period, unavail_only=True
            )

            for up in user_unavailabilities:
                partition.add_slot(
                    TimeInterval(up.start_time, up.end_time),
                    "user_preference",
                    {"value": up.value, "forbidden": True, "tutor": up.user.username},
                )

        else:
            user_availabilities = period_actual_availabilities(
                tutor, period, avail_only=True
            )

            for up in user_availabilities:
                partition.add_slot(
                    TimeInterval(up.start_time, up.end_time),
                    "user_preference",
                    {"value": up.value, "available": True, "tutor": up.user.username},
                )

        partition.tutor_supp = False

        return partition


def coloration_ordered(basic_group):
    """
    Function taking a group and returning all the transversal groups
    in conflict with it colored to avoid to count several times parallel ones


    Parameter:
        basic_group (StructuralGroup): a basic structural group

    Returns :
        tuple: None if no TransversalGroups is found for 'basic_group'
        or tuple(dictionnary, color_max) with the dictionnary
        representing a graph of those TransversalGroups colored according to this pattern:
            {
                transversal_group_1: {
                                        "adjacent" : [tr1, tr2, tr3...]
                                        "color" : int
                                        }
                transversal_group_2: {
                                        "adjacen" : [tr1, tr2, tr3...]
                                        "color" : int
                                        }
                ....
            }
    """
    transversal_conflict_groups = basic_group.transversal_conflicting_groups
    if transversal_conflict_groups:
        graph = []
        for tr in transversal_conflict_groups:
            graph.append(
                (
                    tr,
                    [
                        t
                        for t in transversal_conflict_groups
                        if t != tr and t not in tr.parallel_groups.all()
                    ],
                    0,
                )
            )
        graph.sort(key=lambda x: -len(x[1]))
        graph_dict = {}
        for summit in graph:
            graph_dict[summit[0]] = {"adjacent": summit[1], "color": summit[2]}

        color_max = 0
        for summit, summit_dict in graph_dict.items():
            color_adj = set()
            for adj in summit_dict["adjacent"]:
                color_adj.add(graph_dict[adj]["color"])
            i = 1
            while i in color_adj:
                i += 1
            summit_dict["color"] = i
            color_max = max(color_max, i)
        return graph_dict, color_max
    return None