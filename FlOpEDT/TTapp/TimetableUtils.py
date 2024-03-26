# coding:utf-8

# !/usr/bin/python

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
import json

from django.core.cache import cache
from django.db.models import Count, F, Max, Q
from django.utils.translation import gettext_lazy as _

import base.views as base_views
from base.models import (Course, CourseModification, CourseStartTimeConstraint,
                         CourseType, Department, Module, Room,
                         RoomAvailability, ScheduledCourse, SchedulingPeriod,
                         TimeGeneralSettings, TimetableVersion, TrainingPeriod,
                         TrainingProgramme, UserAvailability)
from base.timing import days_index, str_slot
from people.models import Tutor
from TTapp.FlopConstraint import max_weight
from TTapp.models import MinNonPreferedTrainProgsSlot, MinNonPreferedTutorsSlot
from TTapp.RoomModel import RoomModel
from TTapp.slots import slot_pause


def basic_reassign_rooms(department, period, version, create_new_version):
    msg = {"status": "OK", "more": _("Reload...")}
    result_version = RoomModel(department.abbrev, [period], version).solve(
        create_new_version=create_new_version
    )
    if result_version is not None:
        if create_new_version:
            msg["more"] = _(f"Saved in copy {result_version}")
        else:
            cache.delete(
                base_views.get_key_course_pl(department.abbrev, period, result_version)
            )
    else:
        msg["status"] = "KO"
        msg["more"] = _("Impossible to assign rooms")
    return msg


def get_shared_tutors(department, period, version):
    """
    Returns tutors that are busy both in the department for the given period (version version)
    and in another department (version 0)
    """
    busy_tutors_in_dept = [
        s.tutor
        for s in ScheduledCourse.objects.select_related(
            "course__module__train_prog__department", "tutor"
        )
        .filter(
            course__module__train_prog__department__abbrev=department,
            course__period=period,
            version=version,
        )
        .distinct("tutor")
    ]
    return [
        s.tutor.username
        for s in ScheduledCourse.objects.select_related(
            "course__module__train_prog__department"
        )
        .exclude(course__module__train_prog__department__abbrev=department)
        .filter(course__period=period, tutor__in=busy_tutors_in_dept, version__major=0)
        .distinct("tutor")
    ]


def get_shared_rooms():
    """
    Returns the rooms that are shared between departments
    """
    return Room.objects.annotate(num_depts=Count("departments")).filter(num_depts__gt=1)


def compute_conflicts_helper(dic):
    """
    Computes overlapping slots
    """
    conflicts = []
    for k in dic:
        dic[k].sort(key=lambda s: (s["start_time"]))
    for t, sched_list in dic.items():
        for i in range(len(sched_list) - 1):
            if (
                sched_list[i]["start_time"] + sched_list[i]["duration"]
                > sched_list[i + 1]["start_time"]
            ):
                conflicts.append((sched_list[i], sched_list[i + 1]))
    return conflicts


def compute_conflicts(department, period, version):
    """
    Computes the conflicts (tutor giving several courses at the same time or
    room used in parallel) in period between the work copy copy_a
    of department department, and work copy 0 of the other departments.
    """
    conflicts = {}

    # tutors with overlapping courses
    dic_by_tutor = {}
    tmp_conflicts = []
    tutors_username_list = get_shared_tutors(department, period, version)
    courses_list = (
        ScheduledCourse.objects.select_related(
            "course__module__train_prog__department", "course__duration", "tutor"
        )
        .filter(
            Q(version=version)
            & Q(course__module__train_prog__department__abbrev=department)
            | Q(version__major=0)
            & ~Q(course__module__train_prog__department__abbrev=department),
            course__period=period,
            tutor__username__in=tutors_username_list,
        )
        .annotate(duration=F("course__duration"), period=F("course__period"))
        .values("id", "period", "start_time", "duration", "tutor__username")
    )
    for t in tutors_username_list:
        dic_by_tutor[t] = []
    for sc in courses_list:
        dic_by_tutor[sc["tutor__username"]].append(sc)
    conflicts["tutor"] = compute_conflicts_helper(dic_by_tutor)

    # rooms that are used in parallel
    tmp_conflicts = []
    dic_by_room = {}
    dic_subrooms = {}
    conflict_room_list = get_shared_rooms()

    for room in conflict_room_list:
        dic_subrooms[str(room.id)] = [r.name for r in room.related_rooms()]
    print(dic_subrooms)
    courses_list = (
        ScheduledCourse.objects.select_related("course__duration")
        .filter(Q(course__module__train_prog__department__abbrev=department),
            course__period=period,
            version=version,
            room__in=conflict_room_list,
        )
        .annotate(duration=F("course__duration"), period=F("course__period"))
        .values("id", "start_time", "duration", "room")
    )
    for room in get_shared_rooms():
        dic_by_room[room.name] = []

    # create busy slots for every room in the roomgroups
    for sc in courses_list:
        roomgroup = sc["room"]
        for subroom in dic_subrooms[str(roomgroup)]:
            if subroom in dic_by_room:
                new_sc = sc.copy()
                new_sc["room"] = subroom
                dic_by_room[new_sc["room"]].append(new_sc)

    conflicts["room"] = compute_conflicts_helper(dic_by_room)

    return conflicts


def get_conflicts(department, period, copy_a):
    """
    Checks whether the work copy copy_a of department department is compatible
    with the work copies 0 of the other departments.
    Returns a result {'status':'blabla', 'more':'explanation'}
    """
    result = {"status": "OK"}
    more = ""

    conflicts = compute_conflicts(department, period, copy_a)

    if len(conflicts["tutor"]) + len(conflicts["room"]) == 0:
        return result

    if len(conflicts["tutor"]) > 0:
        more += "Prof déjà occupé·e : "
        for conflict in conflicts["tutor"]:
            sched = []
            for sc in conflict:
                sched.append(ScheduledCourse.objects.get(id=sc["id"]))
            more += sc["tutor__username"] + " : "
            str_sched = list(
                map(
                    lambda s: f"{str_slot(s.day,s.start_time,s.course.duration)} "
                    + f"({s.course.module.abbrev}, {s.course.module.train_prog.department.abbrev})",
                    sched,
                )
            )
            more += " VS ".join(str_sched) + " ; "

    if len(conflicts["room"]) > 0:
        more += "Salle déjà prise : "
        for conflict in conflicts["room"]:
            sched = []
            for sc in conflict:
                sched.append(ScheduledCourse.objects.get(id=sc["id"]))
            str_sched = list(
                map(
                    lambda s: f"{s.room} ({str_slot(s.day,s.start_time,s.course.duration)}, "
                    + f'{s.tutor.username if s.tutor is not None else "No one"}, '
                    + f"{s.course.module.train_prog.department.abbrev})",
                    sched,
                )
            )
            more += " VS ".join(str_sched) + " ; "

    result["status"] = "KO"
    result["more"] = more

    return result


def basic_swap_version(department, period, version_a, version_b):
    version_a.major, version_b.major =  version_b.major, version_a.major
    version_a.save()
    version_b.save()
    cache.delete(base_views.get_key_course_pl(department.abbrev, period, version_a))
    cache.delete(base_views.get_key_course_pl(department.abbrev, period, version_b))
    cache.delete(base_views.get_key_course_pp(department.abbrev, period, version_a))
    cache.delete(base_views.get_key_course_pp(department.abbrev, period, version_b))


def basic_delete_version(department, period, version):

    result = {"status": "OK", "more": ""}

    version.delete()

    cache.delete(base_views.get_key_course_pl(department.abbrev, period, version))

    return result


def basic_delete_all_unused_versions(department, period):
    result = {"status": "OK", "more": ""}
    TimetableVersion.objects.filter(department=department, period=period, version__major__gt=0).delete()
    return result


def basic_duplicate_version(department, period, version):

    result = {"status": "OK", "more": ""}
    scheduled_courses_params = {
        "course__module__train_prog__department": department,
        "course__period": period,
    }
    local_max_major = ScheduledCourse.objects.filter(**scheduled_courses_params).aggregate(
        Max("version__major")
    )["version__major__max"]
    target_major = local_max_major + 1
    target_version = TimetableVersion.objects.create(department=department, period=period, major=target_major)

    try:
        sc_to_duplicate = ScheduledCourse.objects.filter(
            **scheduled_courses_params, version=version
        )
    except KeyError:
        result["status"] = "KO"
        result["more"] = "No scheduled courses"
        return result

    for sc in sc_to_duplicate:
        sc.pk = None
        sc.version = target_version
        sc.save()
    result["status"] = f"Duplicated to version #{target_major}"

    return result


def add_generic_constraints_to_database(department):
    # first objective  => minimise use of unpreferred slots for teachers
    # ponderation MIN_UPS_I

    M, created = MinNonPreferedTutorsSlot.objects.get_or_create(
        weight=max_weight, department=department
    )
    M.save()

    # second objective  => minimise use of unpreferred slots for courses
    # ponderation MIN_UPS_C

    M, created = MinNonPreferedTrainProgsSlot.objects.get_or_create(
        weight=max_weight, department=department
    )
    M.save()


def int_or_none(value):
    if value == "":
        return
    else:
        return value


def load_dispos(json_filename):
    data = json.loads(open(json_filename, "r").read())
    exceptions = set()
    for dispo in data:
        try:
            tutor = Tutor.objects.get(username=dispo["prof"])
        except Tutor.DoesNotExist:
            exceptions.add(dispo["prof"])
            continue
        dispo["date"]
        U, created = UserAvailability.objects.get_or_create(
            user=tutor,
            date = dispo["date"],
            start_time=dispo["start_time"],
            duration=dispo["duration"],
        )
        U.value = dispo["value"]
        U.save()

    if exceptions:
        print("The following tutor do not exist:", exceptions)


def duplicate_what_can_be_in_other_periods(department, period:SchedulingPeriod, version):
    result = {"status": "OK", "more": ""}
    try:
        sched_period = ScheduledCourse.objects.filter(
            course__type__department=department, course__period=period, version=version
        )
        other_periods_courses = Course.objects.filter(
            type__department=department
        ).exclude(period=period)
        other_periods = set(c.period for c in other_periods_courses.distinct("period"))
        period_dates = period.dates()
        for op in other_periods:
            other_period_dates = op.dates()
            if len(period_dates) != (other_period_dates):
                continue
            done = False
            target_version = first_free_version(department, op)
            courses_op = set(other_periods_courses.filter(period=op))
            for i, date in enumerate(period_dates):
                other_date = other_period_dates[i]
                for sc in sched_period.filter(start_time__date=date):
                    filtered_c_ow = [c for c in courses_op if sc.course.equals(c)]
                    if filtered_c_ow:
                        corresponding_course = filtered_c_ow[0]
                        courses_op.remove(corresponding_course)
                        sc.pk = None
                        sc.course = corresponding_course
                        sc.version = target_version
                        sc.start_time = dt.datetime.combine(other_date, sc.start_time.time())
                        sc.save()
                        done = True
                if done:
                    result["more"] += _("%s, ") % op
        return result
    except:
        result["status"] = "KO"
        return result


def first_free_version(department, period):
    local_max_major = ScheduledCourse.objects.filter(
        course__period=period, course__type__department=department
    ).aggregate(Max("version__major"))["version__major__max"]
    if local_max_major is not None:
        target_major = local_max_major + 1
    else:
        target_major = 0
    return TimetableVersion.objects.create(department=department, period=period, major=target_major)


def convert_into_set(declared_object_or_iterable):
    if hasattr(declared_object_or_iterable, "__iter__"):
        return set(declared_object_or_iterable)
    else:
        return {declared_object_or_iterable}


def intersect_with_declared_objects(considered_queryset, declared_object_or_iterable):
    result_set = considered_queryset
    if declared_object_or_iterable is not None:
        result_set = set(result_set) & convert_into_set(declared_object_or_iterable)
    return result_set


def sorted_by_start_time(scheduled_courses_iterable):
    sc_list = list(scheduled_courses_iterable)
    return sorted(
        sc_list, key=lambda x: (x.start_time)
    )


def number_courses(
    department,
    modules=None,
    course_types=None,
    training_periods=None,
    train_progs=None,
    periods=None,
    version_major=0,
):
    considered_train_progs = intersect_with_declared_objects(
        TrainingProgramme.objects.filter(department=department), train_progs
    )
    considered_periods = intersect_with_declared_objects(
        TrainingPeriod.objects.filter(department=department), training_periods
    )
    considered_modules = intersect_with_declared_objects(
        Module.objects.filter(
            train_prog__in=considered_train_progs, training_period__in=considered_periods
        ),
        modules,
    )
    considered_course_types = intersect_with_declared_objects(
        CourseType.objects.filter(department=department), course_types
    )
    for module in considered_modules:
        for course_type in considered_course_types:
            considered_courses = Course.objects.filter(module=module, type=course_type)
            for c_group in considered_courses.distinct("groups"):
                group = c_group.groups.first()
                group_courses = considered_courses.filter(groups=group)
                total_number = len(group_courses)
                if periods is not None:
                    first_period = min(periods, key=lambda x: x.start_date)
                    last_period = max(periods, key=lambda x: x.end_date)
                    group_courses = group_courses.filter(period__gte=first_period, period__lte=last_period)
                    past_courses_number = len(group_courses.filter(period__lt=first_period))
                else:
                    past_courses_number = 0
                sorted_sched_courses = sorted_by_start_time(
                    ScheduledCourse.objects.filter(
                        course__in=group_courses, version__major=version_major
                    )
                )
                for i, sc in enumerate(sorted_sched_courses):
                    sc.number = past_courses_number + i + 1
                    sc.save()

def print_differences(department, periods, old_major, new_major, tutors=Tutor.objects.all()):
    for period in periods:
        print("For", period)
        for tutor in tutors:
            SCa = ScheduledCourse.objects.filter(course__tutor=tutor, version__major=old_major, course__period=period,
                                                 course__type__department=department)
            SCb = ScheduledCourse.objects.filter(course__tutor=tutor, version__major=new_major, course__period=period,
                                                 course__type__department=department)
            slots_a = set([x.start_time for x in SCa])
            slots_b = set([x.start_time for x in SCb])
            if slots_a ^ slots_b:
                result = "For %s old copy has :" % tutor
                for sl in slots_a - slots_b:
                    result += "%s, " % str(sl)
                result += "and new copy has :"
                for sl in slots_b - slots_a:
                    result += "%s, " % str(sl)
                print(result)
