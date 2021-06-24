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


from FlOpEDT.TTapp.TTConstraints.test import TimeInterval, UserPreference
from base.models import TimeGeneralSettings
from django.db import models

from TTapp.TTConstraint import TTConstraint
from TTapp.ilp_constraints.constraint import Constraint
from TTapp.ilp_constraints.constraint_type import ConstraintType
from TTapp.ilp_constraints.constraints.instructorConstraint import InstructorConstraint
from TTapp.ilp_constraints.constraints.slotInstructorConstraint import SlotInstructorConstraint
from TTapp.ilp_constraints.constraints.simulSlotGroupConstraint import SimulSlotGroupConstraint
from TTapp.ilp_constraints.constraints.courseConstraint import CourseConstraint
from django.utils.translation import gettext as _
from TTapp.slots import slots_filter
from TTapp.TTConstraints.groups_constraints import considered_basic_groups, pre_analysis_considered_basic_groups
from base.models import Course, ScheduledCourse
from base.partition import Partition
from base.timing import Day, flopdate_to_datetime

class NoSimultaneousGroupCourses(TTConstraint):
    """
    Only one course for each considered group on simultaneous slots
    """
    groups = models.ManyToManyField('base.StructuralGroup', blank=True)

    def pre_analyse(self, week):

        considered_basic_groups = pre_analysis_considered_basic_groups(self)

        for bg in considered_basic_groups:

            time_settings = TimeGeneralSettings.objects.filter(department = bg.type.department)
            day_start_week = Day(time_settings.days[0], week)
            day_end_week = Day(time_settings.days[len(time_settings.days)-1], week)
            start_week = flopdate_to_datetime(day_start_week, time_settings.day_start_time)
            end_week = flopdate_to_datetime(day_end_week, time_settings.day_finish_time)

            group_partition = Partition(
                "GroupPartition",
                start_week,
                end_week,
                time_settings.day_start_time,
                time_settings.day_finish_time
            )
            group_partition.add_lunch_break(time_settings.lunch_break_start_time, time_settings.lunch_break_finish_time)
            group_partition.add_week_end(time_settings.days)
            considered_courses = set(c for c in Course.objects.filter(week=week, groups__in=bg.and_ancestors()))
            course_dict = dict()
            for c in considered_courses:
                if c.type.duration in course_dict:
                    course_dict[c.type.duration] += 1
                else:
                    course_dict[c.type.duration] = 1 

            course_time_needed = sum(c.type.duration for c in considered_courses)
            if course_time_needed > group_partition.available_duration:
                return False
            else:
                for duration, nb_courses in course_dict.items():
                    if group_partition.nb_slots_of_duration(duration) < nb_courses:
                        return False
        return True

    def enrich_model(self, ttmodel, week, ponderation=1):
        relevant_slots = slots_filter(ttmodel.wdb.availability_slots, week=week)
        relevant_basic_groups = considered_basic_groups(self, ttmodel)
        n_tg = ttmodel.wdb.transversal_groups.count()
        for sl in relevant_slots:
            for bg in relevant_basic_groups:
                relevant_sum = n_tg * ttmodel.sum(ttmodel.TT[(sl2, c2)]
                                               for sl2 in slots_filter(ttmodel.wdb.courses_slots,
                                                                       simultaneous_to=sl)
                                                    for c2 in ttmodel.wdb.courses_for_basic_group[bg]
                                                    & ttmodel.wdb.compatible_courses[sl2]) \
                               + ttmodel.sum(ttmodel.TT[(sl2, c2)]
                                               for tg in ttmodel.wdb.transversal_groups_of[bg]
                                               for sl2 in slots_filter(ttmodel.wdb.courses_slots,
                                                                       simultaneous_to=sl)
                                               for c2 in ttmodel.wdb.courses_for_group[tg]
                                               & ttmodel.wdb.compatible_courses[sl2])
                if self.weight is None:
                    ttmodel.add_constraint(relevant_sum,
                                           '<=', n_tg, SimulSlotGroupConstraint(sl, bg))
                else:
                    two_courses = ttmodel.add_floor(relevant_sum, n_tg + 1, n_tg * len(relevant_slots))
                    ttmodel.add_to_group_cost(bg, self.local_weight() * ponderation * two_courses, week)

            for tg in ttmodel.wdb.transversal_groups:
                relevant_sum_for_tg = ttmodel.sum(ttmodel.TT[(sl2, c2)]
                                                  for sl2 in slots_filter(ttmodel.wdb.courses_slots,
                                                                          simultaneous_to=sl)
                                                  for c2 in ttmodel.wdb.courses_for_group[tg]
                                                  & ttmodel.wdb.compatible_courses[sl2]) \
                                      + ttmodel.sum(ttmodel.TT[(sl2, c2)]
                                                    for tg2 in ttmodel.wdb.not_parallel_transversal_groups[tg]
                                                    for sl2 in slots_filter(ttmodel.wdb.courses_slots,
                                                                            simultaneous_to=sl)
                                                    for c2 in ttmodel.wdb.courses_for_group[tg2]
                                                    & ttmodel.wdb.compatible_courses[sl2])
                if self.weight is None:
                    ttmodel.add_constraint(relevant_sum_for_tg,
                                           '<=', 1, SimulSlotGroupConstraint(sl, tg))
                else:
                    two_courses = ttmodel.add_floor(relevant_sum_for_tg, 2, len(relevant_slots))
                    ttmodel.add_to_global_cost(self.local_weight() * ponderation * two_courses, week)

    def one_line_description(self):
        text = f"Les cours "
        if self.groups.exists():
            text += ' des groupes ' + ', '.join([group.name for group in self.groups.all()])
        else:
            text += " de chaque groupe"
        if self.train_progs.exists():
            text += ' de ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        text += " ne peuvent pas être simultanés"
        return text

    def __str__(self):
        return _("No simultaneous courses for one group")


class ScheduleAllCourses(TTConstraint):
    """
    The considered courses are scheduled, and only once
    """
    modules = models.ManyToManyField('base.Module', blank=True)
    groups = models.ManyToManyField('base.StructuralGroup',
                                    blank=True)
    tutors = models.ManyToManyField('people.Tutor', blank=True)
    course_types = models.ManyToManyField('base.CourseType', blank=True)

    #Checks that the number of courses to scheduled if less than
    #the number of slots available
    def pre_analyse(self, week):
        considered_courses = Course.objects.filter(week = week)
        considered_week_partition = Partition("None", flopdate_to_datetime(Day("m", week), 0), flopdate_to_datetime(Day("su", week), 23*60+59))
        if self.tutors.exists():
            considered_courses = set(c for c in considered_courses if c.tutor in self.tutors.all())
            for tutor in self.tutors:
                userpreferences = UserPreference.objects.filter(user = tutor)
                for up in userpreferences:
                    up_day = Day(up.day, up.week)
                    considered_week_partition.add_slot(
                            TimeInterval(flopdate_to_datetime(up_day, up.start_time),
                            flopdate_to_datetime(up_day, up.end_time)),
                            "user_preference",
                            {"value" : up.value, "available" : True, "tutor" : up.user.username}
                        )
                if considered_week_partition.available_duration < sum(c.type.duration for c in considered_courses if c.tutor == tutor):
                    return False
        if self.modules.exists():
            considered_courses = set(c for c in considered_courses if c.module in self.modules.all())        

        if self.course_types.exists():
            considered_courses = set(c for c in considered_courses if c.type in self.course_types.all())
        if self.groups.exists():
            considered_courses = set(c for c in considered_courses if considered_courses.intersection(self.groups))
        

        return considered_week_partition.available_duration >= sum(c.type.duration for c in considered_courses)
                                
    def enrich_model(self, ttmodel, week, ponderation=1):
        relevant_basic_groups = considered_basic_groups(self, ttmodel)
        considered_courses = set(c for bg in relevant_basic_groups
                                 for c in ttmodel.wdb.courses_for_basic_group[bg])
        max_slots_nb = len(ttmodel.wdb.courses_slots)
        if self.modules.exists():
            considered_courses = set(c for c in considered_courses if c.module in self.modules.all())
        if self.tutors.exists():
            considered_courses = set(c for c in considered_courses if c.tutor in self.tutors.all())
        if self.course_types.exists():
            considered_courses = set(c for c in considered_courses if c.type in self.course_types.all())
        for c in considered_courses:
            relevant_sum = ttmodel.sum([ttmodel.TT[(sl, c)] for sl in ttmodel.wdb.compatible_slots[c]])
            if self.weight is None:
                ttmodel.add_constraint(relevant_sum,
                                       '==', 1,
                                       CourseConstraint(c))
            else:
                not_scheduled = ttmodel.add_floor(relevant_sum, 1, max_slots_nb)
                ttmodel.add_to_generic_cost((1-not_scheduled) * self.local_weight() * ponderation, week)

    def one_line_description(self):
        text = f"Planifie tous les cours "
        if self.groups.exists():
            text += ' des groupes ' + ', '.join([group.name for group in self.groups.all()])
        if self.train_progs.exists():
            text += ' de ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        if self.modules.exists():
            text += ' de : ' + ', '.join([str(module) for module in self.modules.all()])
        if self.course_types.exists():
            text += f" de type" + ', '.join([t.name for t in self.course_types.all()])
        if self.tutors.exists():
            text += ' de ' + ', '.join([tutor.username for tutor in self.tutors.all()])
        return text

    def __str__(self):
        return _("Schedule once every considered course")


class AssignAllCourses(TTConstraint):
    """
    The considered courses are assigned to a tutor
    """
    modules = models.ManyToManyField('base.Module', blank=True)
    groups = models.ManyToManyField('base.StructuralGroup',
                                    blank=True)
    course_types = models.ManyToManyField('base.CourseType', blank=True)

    def enrich_model(self, ttmodel, week, ponderation=1):
        relevant_basic_groups = considered_basic_groups(self, ttmodel)
        considered_courses = set(c for bg in relevant_basic_groups
                                 for c in ttmodel.wdb.courses_for_basic_group[bg])
        if self.modules.exists():
            considered_courses = set(c for c in considered_courses if c.module in self.modules.all())
        if self.course_types.exists():
            considered_courses = set(c for c in considered_courses if c.type in self.course_types.all())
        for c in considered_courses:
            for sl in ttmodel.wdb.compatible_slots[c]:
                relevant_sum = ttmodel.sum(ttmodel.TTinstructors[(sl, c, i)]
                                           for i in ttmodel.wdb.possible_tutors[c]) - ttmodel.TT[sl, c]
                if self.weight is None:
                    ttmodel.add_constraint(relevant_sum,
                                           '==', 0,
                                           InstructorConstraint(constraint_type=ConstraintType.COURS_DOIT_AVOIR_PROFESSEUR,
                                                                slot=sl, course=c))
                else:
                    ttmodel.add_constraint(relevant_sum,
                                           '<=', 0,
                                           InstructorConstraint(
                                               constraint_type=ConstraintType.COURS_DOIT_AVOIR_PROFESSEUR,
                                               slot=sl, course=c))
                    assigned = ttmodel.add_floor(relevant_sum, 0, 1000)
                    ttmodel.add_to_generic_cost((1-assigned) * self.local_weight() * ponderation, week)

    def one_line_description(self):
        text = f"Assigne tous les cours "
        if self.groups.exists():
            text += ' des groupes ' + ', '.join([group.name for group in self.groups.all()])
        if self.train_progs.exists():
            text += ' de ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        if self.modules.exists():
            text += ' de : ' + ', '.join([str(module) for module in self.modules.all()])
        if self.course_types.exists():
            text += f" de type" + ', '.join([t.name for t in self.course_types.all()])
        text += f" à un prof."
        return text

    def __str__(self):
        return _("Each course is assigned to one tutor (max)")


class ConsiderTutorsUnavailability(TTConstraint):
    tutors = models.ManyToManyField('people.Tutor', blank=True)


    def pre_analyse(self, week):
        if self.tutors:
            for tutor in self.tutors:
                courses = Course.objects.filter(tutor = tutor, week = week)
                courses_type = set()
                tutor_partition = Partition("UserPreference", flopdate_to_datetime(Day('m', week), 0), flopdate_to_datetime(Day('su', week), 23*60+59))
                user_preferences = UserPreference.objects.filter(user = tutor, week = week)
                for up in user_preferences:
                    up_day = Day(up.day, up.week)
                    tutor_partition.add_slot(
                        TimeInterval(flopdate_to_datetime(up_day, up.start_time),
                        flopdate_to_datetime(up_day, up.end_time)),
                        "user_preference",
                        {"value" : up.value, "available" : True, "tutor" : up.user.username}
                    )
                if tutor_partition.available_duration < sum(c.type.duration for c in courses):
                    return False
                elif courses.exists():
                    courses_type = dict()
                    for course in courses:
                        if not course.type in courses_type:
                            courses_type[course.type.name] = [course]
                        else:
                            courses_type[course.type.name].append(course)

                    for course_type, course_list in courses_type.items():
                        other_departments_sched_courses = ScheduledCourse.objects.filter(tutor = tutor, week = week ,work_copy=0).exclude(type__department=course_list[0].type.department)
                        time_settings = TimeGeneralSettings.objects.get(department = course_list[0].type.department)
                        day_start_week = Day(time_settings.days[0], week)
                        day_end_week = Day(time_settings.days[len(time_settings.days)-1], week)
                        start_week = flopdate_to_datetime(day_start_week, time_settings.day_start_time)
                        end_week = flopdate_to_datetime(day_end_week, time_settings.day_finish_time)
                        course_partition = Partition(
                                course_type.name,
                                start_week,
                                end_week,
                                time_settings.day_start_time,
                                time_settings.day_finish_time
                            )
                        for sc_course in other_departments_sched_courses:
                            course_partition.add_slot(
                                TimeInterval(
                                    flopdate_to_datetime(Day(sc_course.day, week), sc_course.start_time),
                                    flopdate_to_datetime(Day(sc_course.day, week), sc_course.end_time)
                                ),
                                "all",
                                {"scheduled_course" : sc_course.tutor.username, "forbidden" : True}
                            )
                        course_partition.add_lunch_break(time_settings.lunch_break_start_time, time_settings.lunch_break_finish_time)
                        course_partition.add_week_end(time_settings.days)
                        course_partition.add_partition_data_type(tutor_partition, "user_preference")
                        if course_partition.available_duration < (len(course_list)-len(other_departments_sched_courses))*course_list[0].type.duration:
                            return False
                        
        return True

    def enrich_model(self, ttmodel, week, ponderation=1):
        considered_tutors = set(ttmodel.wdb.instructors)
        if self.tutors.exists():
            considered_tutors &= set(self.tutors.all())
        for tutor in considered_tutors:
            if tutor.username == '---':
                continue
            for sl in ttmodel.wdb.availability_slots:
                tutor_relevant_sum = ttmodel.sum(ttmodel.TTinstructors[(sl2, c2, tutor)]
                                                 for sl2 in slots_filter(ttmodel.wdb.courses_slots,
                                                                         simultaneous_to=sl)
                                                 for c2 in ttmodel.wdb.possible_courses[tutor]
                                                 & ttmodel.wdb.compatible_courses[sl2])
                supp_tutor_relevant_sum = ttmodel.sum(ttmodel.TT[(sl2, c2)]
                                                      for sl2 in slots_filter(ttmodel.wdb.courses_slots,
                                                                              simultaneous_to=sl)
                                                      for c2 in ttmodel.wdb.courses_for_supp_tutor[tutor]
                                                      & ttmodel.wdb.compatible_courses[sl2])
                if self.weight is None:
                    ttmodel.add_constraint(tutor_relevant_sum,
                                           '<=', ttmodel.avail_instr[tutor][sl],
                                           SlotInstructorConstraint(sl, tutor))

                    ttmodel.add_constraint(supp_tutor_relevant_sum,
                                           '<=', ttmodel.avail_instr[tutor][sl],
                                           Constraint(constraint_type=ConstraintType.SUPP_TUTOR,
                                                      instructors=tutor, slots=sl))
                else:
                    ttmodel.add_constraint(tutor_relevant_sum,
                                           '<=', 1,
                                           SlotInstructorConstraint(sl, tutor))

                    ttmodel.add_constraint(supp_tutor_relevant_sum,
                                           '<=', 1,
                                           Constraint(constraint_type=ConstraintType.SUPP_TUTOR,
                                                      instructors=tutor, slots=sl))
                    tutor_undesirable_course = ttmodel.add_floor(tutor_relevant_sum,
                                                                 ttmodel.avail_instr[tutor][sl] + 1,
                                                                 10000)
                    supp_tutor_undesirable_course = ttmodel.add_floor(supp_tutor_relevant_sum,
                                                                      ttmodel.avail_instr[tutor][sl] + 1,
                                                                      10000)
                    ttmodel.add_to_inst_cost(tutor, (tutor_undesirable_course + supp_tutor_undesirable_course)
                                             * self.local_weight() * ponderation, week )

    def one_line_description(self):
        text = f"Considère les indispos"
        if self.tutors.exists():
            text += ' de ' + ', '.join([tutor.username for tutor in self.tutors.all()])
        else:
            text += " de tous les profs."
        return text

    def __str__(self):
        return _("Consider tutors unavailability")