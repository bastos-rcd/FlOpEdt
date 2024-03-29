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
