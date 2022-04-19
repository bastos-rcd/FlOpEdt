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


from core.decorators import timer
from TTapp.TTConstraints.no_course_constraints import NoTutorCourseOnDay
from django.http.response import JsonResponse
from base.timing import TimeInterval
from base.models import CourseStartTimeConstraint
from django.db import models

from TTapp.TTConstraints.TTConstraint import TTConstraint
from TTapp.ilp_constraints.constraint_type import ConstraintType
from TTapp.ilp_constraints.constraints.instructorConstraint import InstructorConstraint
from TTapp.ilp_constraints.constraints.slotInstructorConstraint import SlotInstructorConstraint
from TTapp.ilp_constraints.constraints.simulSlotGroupConstraint import SimulSlotGroupConstraint
from TTapp.ilp_constraints.constraints.courseConstraint import CourseConstraint
from django.utils.translation import gettext as _
from TTapp.slots import slots_filter
from TTapp.TTConstraints.groups_constraints import considered_basic_groups, pre_analysis_considered_basic_groups
from base.models import Course, UserPreference, Holiday
from base.partition import Partition
from base.timing import Day, flopdate_to_datetime
from people.models import Tutor
from django.db.models import Q
from datetime import timedelta

class NoSimultaneousGroupCourses(TTConstraint):
    """
    Only one course for each considered group on simultaneous slots
    """
    groups = models.ManyToManyField('base.StructuralGroup', blank=True)

    @timer
    def pre_analyse(self, week):
        """Pre analysis of the Constraint 
        Compare the available time of the week to the minimum required in any cases (the time of all courses + the time needed for the longest parallel group)
        then to the probable mimimum required (the time of all courses + the time of all parallel groups that are maximum of their graph color) and then
        checks if there is enough available slots for each course type in the week.

        Parameter:
            week (Week): the week we want to analyse the data from
            
        Returns:
            JsonResponse: with status 'KO' or 'OK' and a list of messages explaining the problem"""
        jsondict = {"status" : _("OK"), "messages" : [], "period": { "week": week.nb, "year": week.year }}

        considered_basic_groups = pre_analysis_considered_basic_groups(self)
        for bg in considered_basic_groups:

            #Retrieving information about general time settings and creating the partition
            group_partition = Partition.get_partition_of_week(week, bg.type.department, True)
            
            ### Coloration ###
            tuple_graph = coloration_ordered(bg)
            ### Coloration ###

            #We are looking for the maximum courses' time of transversal groups 
            max_courses_time_transversal = 0
            if tuple_graph:
                graph, color_max = tuple_graph
                for transversal_group in graph:
                    time_courses = transversal_group.time_of_courses(week)
                    if time_courses > max_courses_time_transversal:
                        max_courses_time_transversal = time_courses


            #we are looking for the minimum transversal_groups we need to consider
            transversal_conflict_groups = set()
            if tuple_graph:
                for i in range(1,color_max+1):
                    groups = []
                    for summit, graph_dict in graph.items():
                        if graph_dict["color"] == i:
                            groups.append(summit)

                    group_to_consider = groups[0]
                    time_group_courses = groups[0].time_of_courses(week)
                    for gp in groups:
                        if gp.time_of_courses(week) > time_group_courses:
                            group_to_consider = gp
                            time_group_courses = gp.time_of_courses(week)
                    transversal_conflict_groups.add(group_to_consider)

            #Set of courses for the group and all its structural ancestors
            considered_courses = set(c for c in Course.objects.filter(week=week, groups__in=bg.and_ancestors()))
            #Mimimum time needed in any cases
            min_course_time_needed = sum(c.type.duration for c in considered_courses) + max_courses_time_transversal
            if min_course_time_needed > group_partition.not_forbidden_duration:
                jsondict["status"] = _("KO")
                jsondict["messages"].append({"str":_(f"Group {bg.name} has {group_partition.not_forbidden_duration} available time but requires minimum {min_course_time_needed}."),
                                            "group":bg.id, "type": "NoSimultaneousGroupCourses"})
            else:
                #If they exists we add the transversal courses to the considered_courses
                if transversal_conflict_groups:
                    considered_courses = considered_courses | set(c for c in Course.objects.filter(week=week, groups__in = transversal_conflict_groups))

                #If we are below that amount of time we probably cannot do it.
                course_time_needed = sum(c.type.duration for c in considered_courses)
                if course_time_needed > group_partition.not_forbidden_duration:
                    jsondict["status"] = _("KO")
                    jsondict["messages"].append({"str":_(f"Group {bg.name} has {group_partition.not_forbidden_duration} available time but probably requires minimum {course_time_needed}."),
                                                "group":bg.id, "type": "NoSimultaneousGroupCourses"})
                else:
                    #We are checking if we have enough slots for each course type
                    course_dict = dict()
                    for c in considered_courses:
                        if c.type in course_dict:
                            course_dict[c.type] += 1
                        else:
                            course_dict[c.type] = 1 

                            
                    for course_type, nb_courses in course_dict.items():
                        #We are retrieving the possible start times for each course type and then we check how many we can put in the partition
                        start_times = CourseStartTimeConstraint.objects.get(course_type = course_type)
                        allowed_slots_nb = group_partition.nb_slots_not_forbidden_of_duration_beginning_at(course_type.duration, start_times.allowed_start_times)
                        if allowed_slots_nb < nb_courses:
                            jsondict["status"] = _("KO")
                            jsondict["messages"].append({ "str": _(f"Group {bg.name} has {allowed_slots_nb} slots available of {course_type.duration} minutes and requires {nb_courses}."),
                                                        "group": bg.id, "type": "NoSimultaneousGroupCourses"}) 
        return jsondict

    def enrich_ttmodel(self, ttmodel, week, ponderation=1):
        relevant_slots = slots_filter(ttmodel.wdb.availability_slots, week=week)
        relevant_basic_groups = considered_basic_groups(self, ttmodel)
        # Count the number of transversal groups
        if ttmodel.wdb.transversal_groups.exists():
            n_tg = ttmodel.wdb.transversal_groups.count()
        else:
            n_tg = 1
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
                not_parallel_nb = len(ttmodel.wdb.not_parallel_transversal_groups[tg])
                relevant_sum_for_tg = not_parallel_nb*ttmodel.sum(ttmodel.TT[(sl2, c2)]
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
                                           '<=', not_parallel_nb, SimulSlotGroupConstraint(sl, tg))
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
                                
    def enrich_ttmodel(self, ttmodel, week, ponderation=1):
        relevant_basic_groups = considered_basic_groups(self, ttmodel)
        considered_courses = set(c for bg in relevant_basic_groups
                                 for c in ttmodel.wdb.all_courses_for_basic_group[bg])
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
    If pre_assigned_only, it does assign a tutor only to courses that already have one
    """
    modules = models.ManyToManyField('base.Module', blank=True)
    groups = models.ManyToManyField('base.StructuralGroup',
                                    blank=True)
    course_types = models.ManyToManyField('base.CourseType', blank=True)
    pre_assigned_only = models.BooleanField(default=False, verbose_name=_('Pre-assigned courses only'))

    def enrich_ttmodel(self, ttmodel, week, ponderation=100):
        relevant_basic_groups = considered_basic_groups(self, ttmodel)
        considered_courses = set(c for bg in relevant_basic_groups
                                 for c in ttmodel.wdb.all_courses_for_basic_group[bg])
        if self.pre_assigned_only:
            considered_courses = set(c for c in considered_courses if c.tutor is not None)
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

    @timer
    def pre_analyse(self, week, spec_tutor = None):
        """Pre analysis of the Constraint
        For each tutor considered, checks if he or she has enough time available during the week and then
        if he or she has enough slots for each type of courses
        It takes in consideration the scheduled courses of other departments
        
        Parameters:
            week (Week): the week we want to analyse the data from
            spec_tutor (Tutor): the tutor we want to consider. If None, we'll consider tutors from the constraint

        Returns:
            JsonResponse: with status 'KO' or 'OK' and a list of messages explaining the problem"""
        jsondict = {"status" : _("OK"), "messages" : [], "period": { "week": week.nb, "year": week.year }}
        if spec_tutor:
            considered_tutors = [spec_tutor]
        else:
            considered_tutors = self.tutors.all()

        if not considered_tutors:
            considered_tutors = Tutor.objects.filter(departments = self.department)

        for tutor in considered_tutors:
            courses = Course.objects.filter(Q(tutor = tutor) | Q(supp_tutor = tutor), week = week)
            if not courses.filter(type__department=self.department):
                continue
            tutor_partition = Partition.get_partition_of_week(week, self.department, True)
            user_preferences = UserPreference.objects.filter(user = tutor, week = week, value__gte=1)
            if not user_preferences.exists():
                user_preferences = UserPreference.objects.filter(user = tutor, week = None, value__gte=1)
            for up in user_preferences:
                    up_day = Day(up.day, week)
                    tutor_partition.add_slot(
                        TimeInterval(flopdate_to_datetime(up_day, up.start_time),
                        flopdate_to_datetime(up_day, up.end_time)),
                        "user_preference",
                        {"value" : up.value, "available" : True, "tutor" : up.user.username}
                    )

            if tutor_partition.available_duration < sum(c.type.duration for c in courses):
                message = _(f"Tutor {tutor} has {tutor_partition.available_duration} minutes of available time.")
                message += _(f' He or she has to lecture {len(courses)} classes for an amount of {sum(c.type.duration for c in courses)} minutes of courses.')
                jsondict["messages"].append({ "str": message, "tutor": tutor.id, "type" : "ConsiderTutorsUnavailability"})
                jsondict["status"] = _("KO")

            else:
                no_course_tutor = NoTutorCourseOnDay.objects.filter(Q(tutors = tutor)
                            | Q(tutor_status = tutor.status) | Q(tutors=None), department = self.department,
                            weeks = week)
                if not no_course_tutor:
                    no_course_tutor = NoTutorCourseOnDay.objects.filter(Q(tutors = tutor)
                            | Q(tutor_status = tutor.status) | Q(tutors=None), department = self.department,
                            weeks = None)
                forbidden_days = ""
                if no_course_tutor.exists():
                    for constraint in no_course_tutor:
                        forbidden_days += constraint.weekday+'-'+constraint.period+', '
                        slot = constraint.get_slot_constraint(week, forbidden = True)
                        if slot:
                            tutor_partition.add_slot(
                                slot[0],
                                "no_course_tutor",
                                slot[1]
                            )
                    # we remove the last ','
                    forbidden_days=forbidden_days[:-2]

                holidays = Holiday.objects.filter(week=week)
                holiday_text = ''
                if holidays.exists():
                    for h in holidays:
                        holiday_text += h.day + ', '
                        d = Day(h.day, h.week)
                        start = flopdate_to_datetime(d, 0)
                        end = start + timedelta(days=1)
                        t = TimeInterval(start, end)
                        tutor_partition.add_slot(
                            t,
                            "holiday",
                            {"forbidden" : True}
                        )
                    holiday_text = holiday_text[:-2]

                if tutor_partition.available_duration < sum(c.type.duration for c in courses):
                    message = _(f"Tutor {tutor} has {tutor_partition.available_duration} minutes of available time")
                    if forbidden_days or holiday_text:
                        message += _(f" (considering that")
                        if forbidden_days:
                            message +=_(f" {forbidden_days} is forbidden")
                            if holidays:
                                message += _(f" and {holiday_text} is holiday).")
                            else:
                                message += ').'
                        else:
                            message += _(f" {holiday_text} is holiday).")
                    else:
                        message += '.'
                    message += _(f' He or she has to lecture {len(courses)} classes for an amount of {sum(c.type.duration for c in courses)} minutes of courses.')
                    jsondict["messages"].append({ "str": message, "tutor": tutor.id, "type" : "ConsiderTutorsUnavailability"})
                    jsondict["status"] = _("KO")

                elif courses.exists():
                    # We build a dictionary with the courses' type as keys and list of courses of those types as values
                    courses_type = dict()
                    for course in courses:
                        if not course.type in courses_type:
                            courses_type[course.type] = [course]
                        else:
                            courses_type[course.type].append(course)

                    # For each course type we build a partition with the approriate time settings, the scheduled courses of other departments
                    # and the availabilities of the tutor and we check if the tutor has enough available time and slots.
                    for course_type, course_list in courses_type.items():
                        start_times = CourseStartTimeConstraint.objects.get(course_type=course_type).allowed_start_times
                        course_partition = Partition.get_partition_of_week(week,course_type.department, True)
                        course_partition.add_scheduled_courses_to_partition(week, course_type.department, tutor, True)
                        course_partition.add_partition_data_type(tutor_partition, "user_preference")

                        if course_partition.available_duration < len(course_list)*course_type.duration or course_partition.nb_slots_available_of_duration_beginning_at(course_type.duration, start_times) < len(course_list):
                            message = _(f"Tutor {tutor} has {course_partition.nb_slots_available_of_duration_beginning_at(course_type.duration, start_times)} available slots of {course_type.duration} mins ")
                            message += _(f'and {len(course_list)} courses that long to attend.')
                            jsondict["messages"].append({"str": message, "tutor" : tutor.id, "type" : "ConsiderTutorsUnavailability"})
                            jsondict["status"] = _("KO")
        return jsondict

    def enrich_ttmodel(self, ttmodel, week, ponderation=1):
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
                    ttmodel.add_constraint(tutor_relevant_sum + supp_tutor_relevant_sum,
                                           '<=', ttmodel.avail_instr[tutor][sl],
                                           SlotInstructorConstraint(sl, tutor))
                else:
                    ttmodel.add_constraint(tutor_relevant_sum + supp_tutor_relevant_sum,
                                           '<=', 1,
                                           SlotInstructorConstraint(sl, tutor))

                    tutor_undesirable_course = ttmodel.add_floor(tutor_relevant_sum + supp_tutor_relevant_sum,
                                                                 ttmodel.avail_instr[tutor][sl] + 1,
                                                                 10000)
                    ttmodel.add_to_inst_cost(tutor, tutor_undesirable_course * self.local_weight() * ponderation, week)

    def one_line_description(self):
        text = f"Considère les indispos"
        if self.tutors.exists():
            text += ' de ' + ', '.join([tutor.username for tutor in self.tutors.all()])
        else:
            text += " de tous les profs."
        return text

    def __str__(self):
        return _("Consider tutors unavailability")


def coloration_ordered(basic_group):
    """ Function taking a group and returning all the transversal groups in conflict with it colored to avoid to count several times parallel ones


    Parameter:
        basic_group (StructuralGroup): a basic structural group
    
    Returns : 
        tuple: None if no TransversalGroups is found for 'basic_group' or tuple(dictionnary, color_max) with the dictionnary
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
            graph.append((tr, [t for t in transversal_conflict_groups if t != tr and t not in tr.parallel_groups.all()], 0))
        graph.sort(key = lambda x : -len(x[1]))
        graph_dict = dict()
        for summit in graph:
            graph_dict[summit[0]] = {"adjacent": summit[1], "color" : summit[2]}

        color_max = 0
        for summit, summit_dict in graph_dict.items():
            color_adj = set()
            for adj in summit_dict["adjacent"]:
                color_adj.add(graph_dict[adj]["color"])
            i = 1
            while i in color_adj:
                i+=1
            summit_dict["color"] = i
            if i > color_max:
                color_max = i
        return graph_dict, color_max
    return None