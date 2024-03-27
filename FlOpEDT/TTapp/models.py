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

# pylint: disable=unused-import

import importlib
import inspect
from functools import wraps

from django.conf import settings
from django.db import models
from django.utils.functional import lazy

from TTapp.RoomConstraints.room_constraint import (
    ConsiderRoomSorts,
    LimitedRoomChoices,
    LimitGroupMoves,
    LimitSimultaneousRoomCourses,
    LimitTutorMoves,
    LocateAllCourses,
)
from TTapp.TimetableConstraints.core_constraints import (
    AssignAllCourses,
    ConsiderModuleTutorRepartitions,
    ConsiderTutorsUnavailability,
    NoSimultaneousGroupCourses,
    ScheduleAllCourses,
)
from TTapp.TimetableConstraints.cosmo_style_constraints import (
    LimitHoles,
    LimitTutorTimePerWeeks,
    ModulesByBloc,
)
from TTapp.TimetableConstraints.groups_constraints import (
    GroupsMinHoursPerDay,
    MinGroupsHalfDays,
    MinNonPreferedTrainProgsSlot,
)
from TTapp.TimetableConstraints.limit_time_constraints import (
    LimitCourseTypeTimePerPeriod,
    LimitGroupsTimePerPeriod,
    LimitModulesTimePerPeriod,
    LimitTimePerPeriod,
    LimitTutorsTimePerPeriod,
)
from TTapp.TimetableConstraints.modules_constraints import MinModulesHalfDays
from TTapp.TimetableConstraints.no_course_constraints import (
    NoGroupCourseOnWeekDay,
    NoTutorCourseOnWeekDay,
)
from TTapp.TimetableConstraints.orsay_constraints import (
    BreakAroundCourseType,
    GroupsLunchBreak,
    TutorsLunchBreak,
)
from TTapp.TimetableConstraints.simultaneity_constraints import (
    NotAloneForTheseCouseTypes,
    ParallelizeCourses,
)
from TTapp.TimetableConstraints.slots_constraints import (
    AvoidBothTimesSameDay,
    AvoidStartTimes,
    ConsiderDependencies,
    ConsiderPivots,
    LimitSimultaneousCoursesNumber,
    LimitStartTimeChoices,
    LimitUndesiredSlotsPerDayPeriod,
    SimultaneousCourses,
)
from TTapp.TimetableConstraints.stabilization_constraints import (
    StabilizationThroughPeriods,
    StabilizeGroupsCourses,
    StabilizeTutorsCourses,
)

# Import constraints from other files
from TTapp.TimetableConstraints.timetable_constraint import TimetableConstraint
from TTapp.TimetableConstraints.tutors_constraints import (
    LowerBoundBusyDays,
    MinimizeTutorsBusyDays,
    MinNonPreferedTutorsSlot,
    MinTutorsHalfDays,
    RespectTutorsMaxTimePerDay,
    RespectTutorsMinTimePerDay,
)
from TTapp.TimetableConstraints.visio_constraints import (
    BoundPhysicalPresenceHalfDays,
    Curfew,
    LimitGroupsPhysicalPresence,
    NoVisio,
    VisioOnly,
)

#
#   CustomConstraint
#


def get_constraint_list():
    """
    Return constraint class list contained in CUSTOM_CONSTRAINTS_PATH
    """
    try:
        module = importlib.import_module(settings.CUSTOM_CONSTRAINTS_PATH)
        classes = inspect.getmembers(module, inspect.isclass)

        constraints = []
        for class_name, _ in classes:
            fully_qualified_name = f"{module.__name__}.{class_name}"
            constraints.append((fully_qualified_name, fully_qualified_name))

        return constraints
    except ModuleNotFoundError as exc:
        raise ValueError(
            f"can't find the {settings.CUSTOM_CONSTRAINTS_PATH} module"
        ) from exc


class CustomConstraint(TimetableConstraint):
    """
    Call a custom constraint implementation.
    """

    class_name = models.CharField(max_length=200, null=False, blank=False)
    groups = models.ManyToManyField("base.StructuralGroup", blank=True)
    tutors = models.ManyToManyField("people.Tutor", blank=True)
    modules = models.ManyToManyField("base.Module", blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Delay class_name field choices loading
        self._meta.get_field("class_name").choices = lazy(get_constraint_list, list)()
        self.constraint = None

    def get_constraint(self, class_name):
        """
        Return class_method located in the targeted constraint class instance
        """
        if self.constraint is None:
            module_name, class_name = class_name.rsplit(".", 1)
            try:
                # Get class instance
                module = importlib.import_module(module_name)
                self.constraint = getattr(module, class_name)()
            except ModuleNotFoundError:
                print(f"can't find the <{module_name}> module")
            except:  # pylint: disable=bare-except
                print(f"an error has occured while loading class <{class_name}>")

        return self.constraint

    def get_method(self, method_name):
        """
        Return the method reference by inspecting the constraint instance
        """
        method = None
        constraint = self.get_constraint(self.class_name)
        if constraint:
            method = getattr(constraint, method_name, None)
        return method

    def inject_method(func):
        """
        This decorator lookup for a method, in the class described by
        class_name attribute, with the same name as the decorated method.
        Once retrieve the method is then injected as a method keyword parameter.
        """

        @wraps(func)
        def _wrapper(self, *args, **kwargs):
            method = self.get_method(func.__name__)
            return func(self, *args, injected_method=method, **kwargs)

        return _wrapper

    @inject_method
    def enrich_ttmodel(self, ttmodel, period, ponderation=1, injected_method=None):
        """
        Call custom constraint method
        """
        args = {}

        if self.groups.count():
            args.update({"groups": list(self.groups.all())})

        if self.tutors.count():
            args.update({"tutors": list(self.tutors.all())})

        if self.modules.count():
            args.update({"modules": list(self.modules.all())})

        if self.train_progs.count():
            args.update({"train_progs": list(self.train_progs.all())})

        if injected_method:
            injected_method(ttmodel, ponderation, **args)

    @inject_method
    def one_line_description(self, injected_method=None):
        description = ""
        if injected_method:
            description = injected_method()
            if not description:
                description = self.class_name
        return description

    @inject_method
    def get_viewmodel(self, injected_method=None):
        view_model = super().get_viewmodel()
        details = view_model["details"]
        if injected_method:
            details.update({"class": self.class_name})
            details.update(injected_method())
        else:
            details.update({"class": f"{self.class_name} class not found"})

        return view_model
