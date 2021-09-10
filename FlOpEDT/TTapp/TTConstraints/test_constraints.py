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


from datetime import timedelta
from TTapp.TTConstraints.no_course_constraints import NoTutorCourseOnDay
from base.timing import Day, TimeInterval, flopdate_to_datetime
from django.db import models
from django.http.response import JsonResponse
from django.db.models import Q

from TTapp.TTConstraint import TTConstraint
from TTapp.ilp_constraints.constraint import Constraint
from django.utils.translation import gettext_lazy as _
from base.models import CourseStartTimeConstraint, ModulePossibleTutors, UserPreference


# Vérifier que le cours deux peut être mis après le cours 1
## Vérifier la disponibilité des tutors
## Vérifier les créneaux possibles pour les cours

#if successive : vérifier que la fin du premier peut-être juste après un second
#if ND : vérifier que le premier peut être au minimum un jour avant

def find_successive_slots(course_slot1, course_slot2, course1_duration, course2_duration):
    for cs1 in course_slot1:
        possible_start_time = cs1.start + course1_duration
        for cs2 in course_slot2:
            if cs2.start <= possible_start_time and cs2.end > possible_start_time + course2_duration:
                return True
            if cs2.start > possible_start_time:
                break
    return False

def tutor_and_supp(interval, required_supp, possible_tutors):
    supp_in = False
    tutor_in = False
    if "user_preference" in interval[1]:
        for tutor, value in interval[1]["user_preference"].items():
            if tutor in required_supp and value > 0:
                supp_in = True
            elif tutor in possible_tutors and value > 0:
                tutor_in = True
            if supp_in and tutor_in:
                break
    return supp_in and tutor_in


def find_day_gap_slots(course_slot1, course_slot2, day_gap):
    day_slot = course_slot1[0] + timedelta(days=day_gap) - timedelta(hours=course_slot1[0].hour, minutes=course_slot1[0].minute)
    for cs2 in course_slot2:
        if cs2.start > day_slot:
            return True
    return False


class Precedence(TTConstraint):
    course1 = models.ForeignKey('base.Course', related_name='first', on_delete=models.CASCADE)
    course2 = models.ForeignKey('base.Course', related_name='second', on_delete=models.CASCADE)
    successive = models.BooleanField(verbose_name=_('Successives?'), default=False)
    day_gap = models.PositiveSmallIntegerField(verbose_name=_('Minimal day gap between courses'), default=0)

    def __str__(self):
        return f"{self.course1} avant {self.course2}"

    def pre_analyse(self, week):
        jsondict = {"status" : "OK", "messages" : []}
        week_partition_course1 = self.get_partition_of_week(week, with_day_time=True)
        week_partition_course2 = self.get_partition_of_week(week, with_day_time=True)

        course1_start_times = CourseStartTimeConstraint.objects.get(course_type = self.course1.type).allowed_start_times
        course2_start_times = CourseStartTimeConstraint.objects.get(course_type = self.course2.type).allowed_start_times

        possible_tutors_1 = set()
        required_supp_1 = set()
        if self.course1.tutor is not None:
            possible_tutors_1.add(self.course1.tutor)
        elif ModulePossibleTutors.objects.filter(module = self.course1.module).exists():
            possible_tutors_1 = set(ModulePossibleTutors.objects.get(module = self.course1.module).possible_tutors.all())
        else:
            # A remplacer par tous les tuteurs dispos du département ###
            jsondict['status'] = "KO"
            jsondict['messages'].append(_(f'There is no tutor assigned to {self.course1.full_name()}'))

        if self.course1.supp_tutor is not None:
            required_supp_1 = set(self.course1.supp_tutor.all())


        possible_tutors_2 = set()
        required_supp_2 = set()
        if self.course2.tutor is not None:
            possible_tutors_2.add(self.course2.tutor)
        elif ModulePossibleTutors.objects.filter(module = self.course2.module).exists():
            possible_tutors_2 = set(ModulePossibleTutors.objects.get(module = self.course2.module).possible_tutors.all())
        else:
            # A remplacer par tous les tuteurs dispos du département ###
            jsondict['status'] = "KO"
            jsondict['messages'].append(_(f'There is no tutor assigned to {self.course2.full_name()}'))

        if self.course2.supp_tutor is not None:
            required_supp_2 = set(self.course2.supp_tutor.all())

        print("possible_tutors_1:", possible_tutors_1)
        print("possible_tutors_2:", possible_tutors_2)
        print("required_tutors1:", required_supp_1)
        print("required_tutors2:", required_supp_2)
        if jsondict['status'] == "OK":
            D1 = UserPreference.objects.filter(user__in=possible_tutors_1, week=week, value__gte=1)
            if not D1:
                D1 = UserPreference.objects.filter(user__in=possible_tutors_1, week=None, value__gte=1)

            D2 = UserPreference.objects.filter(user__in=possible_tutors_2, week=week, value__gte=1)
            if not D2:
                D2 = UserPreference.objects.filter(user__in=possible_tutors_2, week=None, value__gte=1)
            
            print("Nb UserPreference_1", len(D1))
            print("Nb UserPreference_2", len(D2))
            #Si on a des préférences possibles pour les deux
            if D1 and D2:
                #On rajoute toutes les User_Preferences à la partition
                no_course_tutor1 = NoTutorCourseOnDay.objects.filter(Q(tutors__in = possible_tutors_1) | Q(tutor_status = [pt.status for pt in possible_tutors_1]), Q(weeks = week) | Q(weeks = None))
                no_course_tutor2 = NoTutorCourseOnDay.objects.filter(Q(tutors__in = possible_tutors_2) | Q(tutor_status = [pt.status for pt in possible_tutors_2]), Q(weeks = week) | Q(weeks = None))
                print("no_course_tutor1", no_course_tutor1)
                print("no_course_tutor2", no_course_tutor2)
                for up in D1:
                    up_day = Day(up.day, week)
                    week_partition_course1.add_slot(
                        TimeInterval(flopdate_to_datetime(up_day, up.start_time),
                        flopdate_to_datetime(up_day, up.end_time)),
                        "user_preference",
                        {"value" : up.value, "available" : True, "tutor" : up.user}
                    )
                for up in D2:
                    up_day = Day(up.day, week)
                    week_partition_course2.add_slot(
                        TimeInterval(flopdate_to_datetime(up_day, up.start_time),
                        flopdate_to_datetime(up_day, up.end_time)),
                        "user_preference",
                        {"value" : up.value, "available" : True, "tutor" : up.user}
                    )

                if required_supp_1:
                    RUS1 = UserPreference.objects.filter(user__in=required_supp_1, week=week, value__gte=1)
                    if not RUS1:
                        RUS1 = UserPreference.objects.filter(user__in=required_supp_1, week=None, value__gte=1)

                    for up in RUS1:
                        up_day = Day(up.day, week)
                        week_partition_course1.add_slot(
                            TimeInterval(flopdate_to_datetime(up_day, up.start_time),
                            flopdate_to_datetime(up_day, up.end_time)),
                            "user_preference",
                            {"value" : up.value, "available" : True, "tutor" : up.user}
                        )

                    for interval in week_partition_course1.intervals:
                        if not tutor_and_supp(interval, required_supp_1, possible_tutors_1):
                            interval[1]["available"] = False



                if required_supp_2:
                    for interval in week_partition_course2.intervals:
                        if tutor_and_supp(interval, required_supp_2, possible_tutors_2):
                            interval[1]["available"] = False
                    RUS2 = UserPreference.objects.filter(user__in=required_supp_2, week=week, value__gte=1)
                    if not RUS2:
                        RUS2 = UserPreference.objects.filter(user__in=required_supp_2, week=None, value__gte=1)
                    for up in RUS2:
                        up_day = Day(up.day, week)
                        week_partition_course2.add_slot(
                            TimeInterval(flopdate_to_datetime(up_day, up.start_time),
                            flopdate_to_datetime(up_day, up.end_time)),
                            "user_preference",
                            {"value" : up.value, "available" : True, "tutor" : up.user}
                        )

                for cs in no_course_tutor1:
                    slot = cs.get_slot_constraint(week)
                    if slot:
                        week_partition_course1.add_slot(
                            slot[0],
                            "all",
                            slot[1]
                        )
                for cs in no_course_tutor2:
                    slot = cs.get_slot_constraint(week)
                    print("course2", slot)
                    if slot:
                        week_partition_course2.add_slot(
                            slot[0],
                            "all",
                            slot[1]
                        )
                print("Partition for course 1:", week_partition_course1)
                print("Partition for course 2:", week_partition_course2)
                course1_slots = week_partition_course1.find_all_available_timeinterval_with_key_starting_at("user_preference", course1_start_times, self.course1.type.duration)
                course2_slots = week_partition_course2.find_all_available_timeinterval_with_key_starting_at("user_preference", course2_start_times, self.course2.type.duration)
                print("Course_slots for course 2:", course2_slots)
                if course1_slots and course2_slots:
                    while course2_slots[0].end < course1_slots[0].start + timedelta(hours = self.course1.type.duration/60, minutes=self.course1.type.duration%60):
                        course2_slots.pop(0)
                        if not course2_slots:
                            break
                    if course2_slots:
                        if course1_slots[0].start + timedelta(hours = self.course1.type.duration/60, minutes=self.course1.type.duration%60) > course2_slots[0].start:
                            course2_slots[0].start = course1_slots[0].start + timedelta(hours = self.course1.type.duration/60, minutes=self.course1.type.duration%60)
                        if len(course2_slots) <= 1 and course2_slots[0].duration < self.course2.type.duration:
                            jsondict["status"] = "KO"
                            jsondict["messages"].append(_('There is no available slots for the second course after the first one.'))
                    else:
                        jsondict["status"] = "KO"
                        jsondict["messages"].append(_('There is no available slots for the second course.'))
                else:
                    jsondict['status'] = "KO"
                    jsondict["messages"].append(_('There is no available slots for the first or the second course.'))

                if jsondict["status"] == "OK":
                    if self.successive:
                        if not find_successive_slots(
                            course1_slots,
                            course2_slots,
                            timedelta(hours = self.course1.type.duration/60, minutes = self.course1.type.duration%60),
                            timedelta(hours = self.course2.type.duration/60, minutes = self.course2.type.duration%60)):
                            jsondict['status'] = "KO"
                            jsondict["messages"].append(_('There is no available successive slots for those courses.'))
                    if self.day_gap != 0:
                        if not find_day_gap_slots(course1_slots, course2_slots, self.day_gap):
                            jsondict['status'] = "KO"
                            jsondict["messages"].append(_(f'There is no available slots for the second course after a {self.day_gap} day gap.'))
            else:
                #Certains utilisateurs n'ont aucunes préférences de renseignées.
                jsondict['status'] = "KO"
                if not D1:
                    jsondict['messages'].append(_(f"There is no available tutor for {self.course1.full_name()}"))
                if not D2:
                    jsondict['messages'].append(_(f"There is no available tutor for {self.course2.full_name()}"))
        return JsonResponse(jsondict)