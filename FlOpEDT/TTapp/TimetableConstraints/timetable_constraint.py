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

from typing import TYPE_CHECKING

from core.decorators import timer
from TTapp.flop_constraint import FlopConstraint
from base.models import StructuralGroup, SchedulingPeriod
from people.models import Tutor

if TYPE_CHECKING:
    from TTapp.timetable_model import TimetableModel


class TimetableConstraint(FlopConstraint):
    """
    Abstract parent class of specific constraints that users may define

    Attributes:
        department : the department concerned by the constraint. Has to be filled.
        periods : the scheduling periods for which the constraint should be applied. All if None.
        weight : from 1 to max_weight if the constraint is optional, depending on its importance
                 None if the constraint is necessary
        is_active : usefull to de-activate a Constraint just before the generation
    """

    class Meta:
        abstract = True

    @timer
    def enrich_ttmodel(
        self, ttmodel: "TimetableModel", period: "SchedulingPeriod", ponderation=1
    ):
        raise NotImplementedError

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        return [
            "department",
        ]

    def get_courses_queryset_by_parameters(
        self,
        period,
        flopmodel: "TimetableModel" = None,
        train_prog=None,
        train_progs=None,
        group=None,
        groups=None,
        transversal_groups_included=False,
        module=None,
        modules=None,
        course_type=None,
        course_types=None,
        room_type=None,
        room_types=None,
        tutor=None,
        tutors=None,
    ):
        courses_qs = FlopConstraint.get_courses_queryset_by_parameters(
            self,
            period,
            flopmodel,
            train_prog=train_prog,
            train_progs=train_progs,
            group=group,
            groups=groups,
            transversal_groups_included=transversal_groups_included,
            module=module,
            modules=modules,
            course_type=course_type,
            course_types=course_types,
            room_type=room_type,
            room_types=room_types,
        )

        # if tutor is not None, we have to reduce to the courses that are in possible_course[tutor]
        if tutor is not None:
            if flopmodel is not None:
                if tutor in flopmodel.data.instructors:
                    courses_qs = courses_qs.filter(
                        id__in=[c.id for c in flopmodel.data.possible_courses[tutor]]
                    )
                courses_qs = courses_qs.filter(id__in=[])
        if tutors:
            considered_tutors = set(tutors) & set(flopmodel.data.instructors)
            if flopmodel is not None:
                courses_qs = courses_qs.filter(
                    id__in=[
                        c.id
                        for tutor in considered_tutors
                        for c in flopmodel.data.possible_courses[tutor]
                    ]
                )

        return courses_qs

    def considered_basic_groups(self, ttmodel=None):
        if ttmodel is None:
            basic_groups = StructuralGroup.objects.filter(
                train_prog__department=self.department, basic=True
            )
        else:
            basic_groups = ttmodel.data.basic_groups
        if hasattr(self, "train_progs"):
            if self.train_progs.exists():
                basic_groups = set(
                    basic_groups.filter(train_prog__in=self.train_progs.all())
                )
            else:
                basic_groups = set(basic_groups)
        if hasattr(self, "groups"):
            if self.groups.exists():
                constraint_basic_groups = set()
                for g in self.groups.all():
                    constraint_basic_groups |= g.basic_groups()
                basic_groups &= constraint_basic_groups
        if ttmodel is None:
            return basic_groups
        ttmodel_basic_groups_to_consider = set()
        for g in basic_groups:
            if ttmodel.data.courses_for_basic_group[g]:
                ttmodel_basic_groups_to_consider.add(g)
        return ttmodel_basic_groups_to_consider

    def considered_groups(self, ttmodel=None, transversal_groups_included=False):
        basic_groups = self.considered_basic_groups(ttmodel)
        result = set()
        for bg in basic_groups:
            result |= bg.and_ancestors()
            if transversal_groups_included:
                result |= bg.transversal_conflicting_groups()
        return result

    def considered_tutors(self, ttmodel: "TimetableModel" = None):
        if ttmodel is None:
            tutors_to_consider = set(Tutor.objects.filter(departments=self.department))
        else:
            tutors_to_consider = set(ttmodel.data.instructors)
        if hasattr(self, "tutors"):
            if self.tutors.exists():
                tutors_to_consider &= set(self.tutors.all())
        if hasattr(self, "tutor_status"):
            if self.tutor_status is not None:
                tutors_to_consider &= set(
                    t
                    for t in tutors_to_consider
                    if t.status == self.tutor_status  # pylint: disable=no-member
                )
        return tutors_to_consider