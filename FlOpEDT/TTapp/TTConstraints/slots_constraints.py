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
import TTapp.GlobalPreAnalysis.partition_with_constraints as partition_bis
from datetime import timedelta

from django.http.response import JsonResponse
from base.models import CourseStartTimeConstraint, Dependency
from django.contrib.postgres.fields import ArrayField

from django.db import models
from django.db.models import Q
from base.timing import french_format, Day

from TTapp.ilp_constraints.constraint_type import ConstraintType
from TTapp.ilp_constraints.constraint import Constraint
from TTapp.slots import days_filter, slots_filter, Slot
from TTapp.TTConstraints.TTConstraint import TTConstraint
from TTapp.TTConstraints.core_constraints import ConsiderTutorsUnavailability

from TTapp.ilp_constraints.constraints.dependencyConstraint import DependencyConstraint
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext
from django.core.validators import MaxValueValidator
from TTapp.TTConstraints.tutors_constraints import considered_tutors
from TTapp.TTConstraints.groups_constraints import considered_basic_groups



class SimultaneousCourses(TTConstraint):
    """
    Force courses to start simultaneously
    """
    courses = models.ManyToManyField('base.Course', related_name='simultaneous_courses_constraints')

    def pre_analyse(self,week):
        """
        Pre-analysis of the constraint
        Firstly verify if there is only one course per group/tutor to be done simultaneously
        Then built a partition comparing each tutor availability (Can be optimized)
        At the end, try to find an available slot in the week for the considered_courses

        Parameters :
            week : pre_analyse's current week

        Returns :
            jsondict :  a Json dictionary that contains the result of the pre-analyse
        """
        jsondict = {"status": _("OK"), "messages": [], "period": {"week": week.nb, "year": week.year}}

        # pre_analyse's week simultaneous courses retrieval
        considered_courses = (list(c for c in self.courses.all() if c.week == week ))

        #We verify if there is only one course to do simultaneously for each tutor/group
        jsondict,OK = self.maxOneCourse(jsondict, considered_courses)
        if not(OK) :
            return jsondict

        # No course in the constraint case
        if len(considered_courses) == 0:
            jsondict["status"] = _("KO")
            message = gettext("No partition created : maybe there is no courses or it's wrong the week")
            jsondict["messages"].append({"str": message, "type": "SimultaneousCourses"})
            return jsondict

        # We build a week's partition comparing partition of each tutors
        partition = None
        no_user_pref = not ConsiderTutorsUnavailability.objects.filter(weeks=week).exists()
        for course in considered_courses :
            if partition == None : # Here we build the partition of the first teacher
                partition = partition_bis.create_course_partition_from_constraints(course,week,course.type.department,available=no_user_pref)
            new_partition = partition_bis.create_course_partition_from_constraints(course,week,course.type.department,available=no_user_pref)
            """
            Then, for each interval (named interval1) available and not forbidden of the main partition (named partition) 
            we watch if the interval of another teacher (named interval2) is also available and not forbidden 
            """
            for interval1 in partition.intervals :
                if interval1[1]["available"] and not(interval1[1]["forbidden"]):
                    for interval2 in new_partition.intervals :
                        if not(interval1[0].start >= interval2[0].end\
                                or interval1[0].end <= interval2[0].start) :
                            interval1[1]["available"] = interval2[1]["available"]
                            interval1[1]["forbidden"] = interval2[1]["forbidden"]

        max_duration = 0
        # Here we find the maximal duration of the simultaneous courses
        for course in considered_courses :
            max_duration = max(max_duration,course.type.duration)


        # Here we search for an available slot in the week
        if partition.nb_slots_available_of_duration(max_duration) < 1:
            jsondict["status"] = _("KO")
            message = gettext("Not enough common available time for courses ")
            for course in considered_courses :
                message += " {course} "
            message += " to be done simultaneously"
            jsondict["messages"].append({"str": message, "type": "SimultaneousCourses"})
            jsondict["status"] = _("KO")
        return jsondict

    def maxOneCourse (self, jsondict, consideredCourses):
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
        for course in consideredCourses :
            if (consideredTutors.__contains__(course.tutor)):
                if not(tutorError.__contains__(course.tutor)):
                    tutorError.append(course.tutor)
                    jsondict["status"] = _("KO")
                    message = gettext("Tutor %s has more than one to do at the same time") % course.tutor
                    jsondict["messages"].append({"str": message, "tutor": course.tutor.id, "type": "SimultaneousCourses"})
                    statusOK = False
            consideredTutors.append(course.tutor)
            course_groups = course.groups.all()
            for group in course_groups :
                if consideredGroups.__contains__(group) :
                    if not(groupError.__contains__(group)):
                        groupError.append(group)
                        jsondict["status"] = _("KO")
                        message = gettext("Group %s has more than one course to do at the same time") % group.name
                        jsondict["messages"].append({"str": message, "group": group.id, "type": "SimultaneousCourses"})
                        statusOK = False
                consideredGroups.append(group)
        return jsondict, statusOK

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        courses_weeks = self.courses.all().distinct('week')
        nb = courses_weeks.count()
        if nb == 0:
            return
        else:
            super().save(*args, **kwargs)
            self.weeks.clear()
            for w in courses_weeks:
                self.weeks.add(w.week)


    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(['courses'])
        return attributes

    def enrich_ttmodel(self, ttmodel, week, ponderation=1):
        course_types = set(c.type for c in self.courses.all())
        relevant_courses = set(self.courses.all()) & set(ttmodel.wdb.courses)
        nb_courses = len(relevant_courses)
        if nb_courses < 2:
            return
        possible_start_times = set()
        for t in course_types:
            possible_start_times |= set(t.coursestarttimeconstraint_set.all()[0].allowed_start_times)
        for day in days_filter(ttmodel.wdb.days, week=week):
            for st in possible_start_times:
                check_var = ttmodel.add_var("check_var")
                expr = ttmodel.lin_expr()
                for c in relevant_courses:
                    possible_slots = slots_filter(ttmodel.wdb.compatible_slots[c], start_time=st, day=day)
                    for sl in possible_slots:
                        expr += ttmodel.TT[(sl, c)]
                ttmodel.add_constraint(nb_courses * check_var - expr, '==', 0,
                                       Constraint(constraint_type=ConstraintType.SIMULTANEOUS_COURSES,
                                                  courses=relevant_courses))
                ttmodel.add_constraint(expr - check_var, '>=', 0,
                                       Constraint(constraint_type=ConstraintType.SIMULTANEOUS_COURSES,
                                       courses=relevant_courses))

    def get_viewmodel(self):
        view_model = super().get_viewmodel()
        details = view_model['details']

        if self.courses.exists():
            details.update({'courses': ', '.join([str(course) for course in self.courses.all()])})

        return view_model

    def one_line_description(self):
        return f"Les cours {self.courses.all()} doivent être simultanés !"

    class Meta:
        verbose_name = _('Simultaneous courses')
        verbose_name_plural = verbose_name


class StartTimeConstraint(TTConstraint):
    module = models.ForeignKey('base.Module',
                               null=True,
                               blank=True,
                               default=None,
                               on_delete=models.CASCADE)
    tutor = models.ForeignKey('people.Tutor',
                              null=True,
                              blank=True,
                              default=None,
                              on_delete=models.CASCADE)
    group = models.ForeignKey('base.StructuralGroup',
                              null=True,
                              blank=True,
                              default=None,
                              on_delete=models.CASCADE)
    course_type = models.ForeignKey('base.CourseType',
                                    null=True,
                                    blank=True,
                                    default=None,
                                    on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def excluded_slots(self, ttmodel):
        raise NotImplementedError

    def enrich_ttmodel(self, ttmodel, week, ponderation=1.):
        fc = self.get_courses_queryset_by_attributes(ttmodel, week)
        excluded_slots = self.excluded_slots(ttmodel)
        if self.tutor is None:
            relevant_sum = ttmodel.sum(ttmodel.TT[(sl, c)]
                                       for c in fc
                                       for sl in ttmodel.wdb.compatible_slots[c] & excluded_slots)
        else:
            relevant_sum = ttmodel.sum(ttmodel.TTinstructors[(sl, c, self.tutor)]
                                       for c in fc
                                       for sl in ttmodel.wdb.compatible_slots[c] & excluded_slots)
        if self.weight is not None:
            ttmodel.add_to_generic_cost(self.local_weight() * ponderation * relevant_sum, week=week)
        else:
            ttmodel.add_constraint(relevant_sum, '==', 0,
                                   Constraint(constraint_type=ConstraintType.LIMITED_START_TIME_CHOICES,
                                              instructors=self.tutor, groups=self.group, modules=self.module,))


class LimitStartTimeChoices(StartTimeConstraint):
    """
    Limit the possible start times
    """

    possible_week_days = ArrayField(models.CharField(max_length=2, choices=Day.CHOICES), blank=True, null=True)
    possible_start_times = ArrayField(models.PositiveSmallIntegerField(), blank=True, null=True)

    class Meta:
        verbose_name = _('Limited start time choices')
        verbose_name_plural = verbose_name

    def considered_start_times(self, ttmodel):
        if self.possible_start_times:
            return self.possible_start_times
        return set(sl.start_time for sl in ttmodel.wdb.courses_slots)

    def considered_week_days(self):
        if self.possible_week_days:
            return self.possible_week_days
        return list(c[0] for c in Day.CHOICES)

    def excluded_slots(self, ttmodel):
        return set(sl for sl in ttmodel.wdb.courses_slots
                   if (sl.start_time not in self.considered_start_times(ttmodel)
                       or sl.day.day not in self.considered_week_days()))

    def one_line_description(self):
        text = "Les "
        if self.course_type:
            text += str(self.course_type)
        else:
            text += "cours"
        if self.module:
            text += " de " + str(self.module)
        if self.tutor:
            text += ' de ' + str(self.tutor)
        if self.train_progs.exists():
            text += ' en ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        else:
            text += " pour toutes les promos"
        if self.group:
            text += ' avec le groupe ' + str(self.group)
        text += " ne peuvent avoir lieu que"
        if not (self.possible_week_days or self.possible_start_times):
            text += ' ... Tout le temps!'
        else:
            if self.possible_week_days:
                text += ' les '
                text += ', '.join(self.possible_week_days)
            if self.possible_start_times:
                text += ' à '
                text += ', '.join([french_format(pst) for pst in self.possible_start_times])
        text += '.'
        return text


class AvoidStartTimes(StartTimeConstraint):
    """
    Avoid some start times
    """

    forbidden_week_days = ArrayField(models.CharField(max_length=2, choices=Day.CHOICES), blank=True, null=True)
    forbidden_start_times = ArrayField(models.PositiveSmallIntegerField(), blank=True, null=True)

    class Meta:
        verbose_name = _('Avoid considered start times')
        verbose_name_plural = verbose_name

    def considered_start_times(self, ttmodel):
        if self.forbidden_start_times:
            return self.forbidden_start_times
        return set(sl.start_time for sl in ttmodel.wdb.courses_slots)

    def considered_week_days(self):
        if self.forbidden_week_days:
            return self.forbidden_week_days
        return list(c[0] for c in Day.CHOICES)

    def excluded_slots(self, ttmodel):
        return set(sl for sl in ttmodel.wdb.courses_slots
                   if (sl.start_time in self.considered_start_times(ttmodel)
                       and sl.day.day in self.considered_week_days()))

    def one_line_description(self):
        text = "Les "
        if self.course_type:
            text += str(self.course_type)
        else:
            text += "cours"
        if self.module:
            text += " de " + str(self.module)
        if self.tutor:
            text += ' de ' + str(self.tutor)
        if self.train_progs.exists():
            text += ' en ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        else:
            text += " pour toutes les promos"
        if self.group:
            text += ' avec le groupe ' + str(self.group)
        text += " ne peuvent pas avoir lieu"
        if not (self.forbidden_week_days or self.forbidden_start_times):
            text += ' ... Tout le temps!'
        else:
            if self.possible_week_days:
                text += ' les '
                text += ', '.join(self.forbidden_week_days)
            if self.possible_start_times:
                text += ' à '
                text += ', '.join([french_format(pst) for pst in self.forbidden_start_times])
        text += '.'
        return text


################    ConsiderDependencies FUNCTIONS      ################
def find_successive_slots(course_slot1, course_slot2, course1_duration, course2_duration):
    '''This function returns True if it finds a slot for the second course right after one of the first one with enough
    time duration.
    Complexity on O(n^2): n being the number of slots for each course.

    Parameters:
        course_slot1 (list(TimeInterval)): A list of time interval representing when the first course can be placed
        course_slot2 (list(TimeInterval)): A list of time interval representing when the second course can be placed
        course1_duration (timedelta): The duration of the first course
        course2_duration (timedelta): The duration of the second course

    Returns:
        (boolean): If we found at least one eligible slot'''
    for cs1 in course_slot1:
        possible_start_time = cs1.start + course1_duration
        for cs2 in course_slot2:
            if cs2.start <= cs1.end:
                if cs2.start > possible_start_time and cs2.end >= cs2.start + course2_duration:
                    return True
                elif cs2.start <= possible_start_time and cs2.end >= possible_start_time + course2_duration:
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
        (boolean) : whether there is available time for the second course after the day gap or not"""
    day_slot = course_slots1[0].start + timedelta(days=day_gap) - timedelta(hours=course_slots1[0].start.hour, minutes=course_slots1[0].start.minute)
    for cs2 in course_slots2:
        if cs2.start > day_slot:
            return True
    return False


class ConsiderDependencies(TTConstraint):
    """
    Transform the constraints of dependency saved on the DB in model constraints:
    -include dependencies and successiveness
    -include non same-day constraint
    -include simultaneity (double dependency)
    If there is a weight, it's a preference, else it's a constraint...
    """
    modules = models.ManyToManyField('base.Module', blank=True)

    class Meta:
        verbose_name = _('Consider dependecies')
        verbose_name_plural = verbose_name

    @timer
    def pre_analyse(self, week):
        """Pre analysis of the Constraint
        For each dependency, first checks if there is available slots for both courses taking in consideration tutor's and supp_tutor's
        availabilities, NoTutorCourseOnDay constraints and possible start times. Then we check if we still have slots for the second one
        starting after the first one and then if the options are True and or above 0 we check successive slots and the day gap.

        Parameter:
            week (Week): the week we want to analyse the data from

        Returns:
            JsonResponse: with status 'KO' or 'OK' and a list of messages explaining the problem"""
        dependencies = self.considered_dependecies().filter(course1__week=week, course2__week=week)
        jsondict = {"status" : _("OK"), "messages" : [], "period": { "week": week.nb, "year": week.year} }
        no_user_pref = not ConsiderTutorsUnavailability.objects.filter(Q(weeks=week)|Q(weeks__isnull=True)).exists()
        for dependency in dependencies:
            ok_so_far = True
            # Setting up partitions with data about other constraints for both courses
            week_partition_course1 = partition_bis.create_course_partition_from_constraints(dependency.course1, week,
                                                                                            self.department,
                                                                                            available=no_user_pref)
            week_partition_course2 = partition_bis.create_course_partition_from_constraints(dependency.course2, week,
                                                                                            self.department,
                                                                                            available=no_user_pref)

            if week_partition_course1 and week_partition_course2:
                # Retrieving possible start times for both courses
                course1_start_times = CourseStartTimeConstraint.objects.get(course_type=dependency.course1.type).allowed_start_times
                course2_start_times = CourseStartTimeConstraint.objects.get(course_type=dependency.course2.type).allowed_start_times
                # Retrieving only TimeInterval for each course
                course1_slots = week_partition_course1.find_all_available_timeinterval_starting_at(course1_start_times, dependency.course1.type.duration)
                course2_slots = week_partition_course2.find_all_available_timeinterval_starting_at(course2_start_times, dependency.course2.type.duration)
                if course1_slots and course2_slots:
                    while course2_slots[0].end < course1_slots[0].start + timedelta(hours = dependency.course1.type.duration/60+dependency.course2.type.duration/60):
                        course2_slots.pop(0)
                        if not course2_slots:
                            break
                    if course2_slots:
                        if course1_slots[0].start + timedelta(hours = dependency.course1.type.duration/60) > course2_slots[0].start:
                            course2_slots[0].start = course1_slots[0].start + timedelta(hours = dependency.course1.type.duration/60)
                        # Here we check if the first course_slot that we might just shrank is still long enough and if it is the only
                        # one left.
                        if len(course2_slots) <= 1 and course2_slots[0].duration < dependency.course2.type.duration:
                            jsondict["status"] = _("KO")
                            ok_so_far = False
                            jsondict["messages"].append({ "str" : gettext('There is no available slots for the second course after the first one : %s') % dependency,
                                                            "course1": dependency.course1.id,
                                                            "course2": dependency.course2.id,
                                                            "type" : "ConsiderDependencies" })
                    else:
                        jsondict["status"] = _("KO")
                        ok_so_far = False
                        jsondict["messages"].append({ "str" : gettext('There is no available slots for the second course after the first one : %s') % dependency,
                                                            "course1": dependency.course1.id,
                                                            "course2": dependency.course2.id,
                                                            "type" : "ConsiderDependencies" })
                else:
                    jsondict['status'] = _("KO")
                    ok_so_far = False
                    jsondict["messages"].append({ "str": gettext(f'There is no available slots for the first or the second course : %s') % dependency,
                                                            "course1": dependency.course1.id,
                                                            "course2": dependency.course2.id,
                                                            "type" : "ConsiderDependencies" })

                if ok_so_far:
                    if dependency.successive:
                        if not find_successive_slots(
                            course1_slots,
                            course2_slots,
                            timedelta(hours = dependency.course1.type.duration/60),
                            timedelta(hours = dependency.course2.type.duration/60)):
                            jsondict['status'] = _("KO")
                            ok_so_far = False
                            jsondict["messages"].append({ "str": gettext(f'There is no available successive slots for those courses: %s') % dependency,
                                                            "course1": dependency.course1.id,
                                                            "course2": dependency.course2.id,
                                                            "type" : "ConsiderDependencies" })
                    if dependency.day_gap != 0:
                        if not find_day_gap_slots(course1_slots, course2_slots, dependency.day_gap):
                            jsondict['status'] = _("KO")
                            ok_so_far = False
                            jsondict["messages"].append({ "str": gettext('There is no available slots for the second '
                                                                         'course after a %(day_gap)s day gap: %(dependency)s') % {"day_gap": dependency.day_gap,
                                                                                                                                   "dependency": dependency},
                                                            "course1": dependency.course1.id,
                                                            "course2": dependency.course2.id,
                                                            "type" : "ConsiderDependencies" })
            else:
                jsondict['status'] = _("KO")
                ok_so_far = False
                jsondict["messages"].append({ "str": gettext('One of the courses has no eligible tutor to lecture it: %s') % dependency,
                                                            "course1": dependency.course1.id,
                                                            "course2": dependency.course2.id,
                                                            "type" : "ConsiderDependencies" })
        return jsondict

    def considered_dependecies(self):
        """Returns the dependencies that have to be considered"""
        result=Dependency.objects.filter(course1__type__department=self.department, course2__type__department=self.department)
        if self.train_progs.exists():
            result = result.filter(course1__module__train_prog__in=self.train_progs.all(), course2__module__train_prog__in=self.train_progs.all())
        if self.modules.exists():
            result = result.filter(course1__module__in=self.modules.all(), course2__module__in=self.modules.all())
        if self.weeks.exists():
            result = result.filter(course1__week__in=self.weeks.all(), course2__week__in=self.weeks.all())
        return result

    def one_line_description(self):
        text = f"Prend en compte les précédences enregistrées en base."
        if self.train_progs.exists():
            text += ' des promos ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        if self.modules.exists():
            text += ' pour les modules ' + ', '.join([module.abbrev for module in self.modules.all()])
        return text

    def enrich_ttmodel(self, ttmodel, week, ponderation=10):
        if self.train_progs.exists():
            train_progs = set(tp for tp in self.train_progs.all() if tp in ttmodel.train_prog)
        else:
            train_progs = set(ttmodel.train_prog)
        considered_modules = set(ttmodel.wdb.modules)
        if self.modules.exists():
            considered_modules &= set(self.modules.all())

        for p in ttmodel.wdb.dependencies:
            c1 = p.course1
            c2 = p.course2
            if (c1.module not in considered_modules and c2.module not in considered_modules) or \
                    (c1.module.train_prog not in train_progs and c2.module.train_prog not in train_progs):
                continue
            if c1 == c2:
                ttmodel.add_warning(None, "Warning: %s is declared depend on itself" % c1)
                continue
            for sl1 in ttmodel.wdb.compatible_slots[c1]:
                if not self.weight:
                    ttmodel.add_constraint(1000000 * ttmodel.TT[(sl1, c1)] +
                                           ttmodel.sum(ttmodel.TT[(sl2, c2)] for sl2 in ttmodel.wdb.compatible_slots[c2]
                                                       if not sl2.is_after(sl1)
                                                       or (p.ND and (sl2.day == sl1.day))
                                                       or (p.successive and not sl2.is_successor_of(sl1))),
                                           '<=', 1000000, DependencyConstraint(c1, c2, sl1))
                else:
                    for sl2 in ttmodel.wdb.compatible_slots[c2]:
                        if not sl2.is_after(sl1) \
                                or (p.ND and (sl2.day == sl1.day)) \
                                or (p.successive and not sl2.is_successor_of(sl1)):
                            conj_var = ttmodel.add_conjunct(ttmodel.TT[(sl1, c1)],
                                                            ttmodel.TT[(sl2, c2)])
                            ttmodel.add_to_generic_cost(conj_var * self.local_weight() * ponderation)


class ConsiderPivots(TTConstraint):
    """
    Transform the constraints of pivots saved on the DB in model constraints:
    -include non same-day constraint
    If there is a weight, it's a preference, else it's a constraint...
    """
    modules = models.ManyToManyField('base.Module', blank=True)

    class Meta:
        verbose_name = _('Consider pivots')
        verbose_name_plural = verbose_name

    def one_line_description(self):
        text = f"Prend en compte les pivots enregistrées en base."
        if self.train_progs.exists():
            text += ' des promos ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        if self.modules.exists():
            text += ' pour les modules ' + ', '.join([module.abbrev for module in self.modules.all()])
        return text

    def enrich_ttmodel(self, ttmodel, week, ponderation=10):
        if self.train_progs.exists():
            train_progs = set(tp for tp in self.train_progs.all() if tp in ttmodel.train_prog)
        else:
            train_progs = set(ttmodel.train_prog)
        considered_modules = set(ttmodel.wdb.modules)
        if self.modules.exists():
            considered_modules &= set(self.modules.all())

        for p in ttmodel.wdb.pivots:
            pivot = p.pivot_course
            other = p.other_courses.all()
            other_length = other.count()
            if (pivot.module not in considered_modules
                and all (o.module not in considered_modules for o in other)) or \
                    (pivot.module.train_prog not in train_progs
                     and all (o.module.train_prog not in train_progs for o in other)):
                continue
            if pivot in other:
                ttmodel.add_warning(None, f"Warning: {pivot} is declared pivoting around itself")
                continue
            for sl1 in ttmodel.wdb.compatible_slots[pivot]:
                all_after = ttmodel.add_floor(ttmodel.sum(ttmodel.TT[(sl2, o)]
                                                          for o in other
                                                          for sl2 in ttmodel.wdb.compatible_slots[o]
                                                          if (not p.ND and not sl2.is_after(sl1))
                                                          or (p.ND and (sl1.has_previous_day_than(sl2)))
                                                          ),
                                              other_length, 2 * other_length)
                all_before = ttmodel.add_floor(ttmodel.sum(ttmodel.TT[(sl2, o)]
                                                           for o in other
                                                           for sl2 in ttmodel.wdb.compatible_slots[o]
                                                           if (not p.ND and not sl1.is_after(sl2))
                                                           or (p.ND and (sl2.has_previous_day_than(sl1)))
                                                           ),
                                               other_length, 2 * other_length)
                if not self.weight:
                    ttmodel.add_constraint(ttmodel.TT[(sl1, pivot)] - all_after - all_before,
                                           '<=', 0, Constraint(constraint_type=ConstraintType.PIVOT,
                                                              slots=sl1))
                else:
                    undesired_situation = ttmodel.add_floor(10 * ttmodel.TT[(sl1, pivot)] - all_after - all_before,
                                                            10,
                                                            20)

                    ttmodel.add_to_generic_cost(undesired_situation * self.local_weight() * ponderation)


# Ex TTConstraints that have to be re-written.....


class AvoidBothTimesSameDay(TTConstraint):
    """
    Avoid the use of two slots
    Idéalement, on pourrait paramétrer slot1, et slot2 à partir de slot1... Genre slot1
    c'est 8h n'importe quel jour, et slot2 14h le même jour...
    """
    time1 = models.PositiveSmallIntegerField()
    time2 = models.PositiveSmallIntegerField()
    weekdays = ArrayField(models.CharField(max_length=2, choices=Day.CHOICES), blank=True, null=True)
    groups = models.ManyToManyField('base.StructuralGroup', blank=True)

    class Meta:
        verbose_name = _('Avoid using both times on same day')
        verbose_name_plural = verbose_name

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(['groups'])
        return attributes


    def enrich_ttmodel(self, ttmodel, week, ponderation=1):
        considered_groups = considered_basic_groups(self, ttmodel)
        days = days_filter(ttmodel.wdb.days, week=week)
        slots1 = set([slot for slot in ttmodel.wdb.courses_slots
                      if slot.start_time <= self.time1 < slot.end_time])
        slots2 = set([slot for slot in ttmodel.wdb.courses_slots
                      if slot.start_time <= self.time2 < slot.end_time])
        if self.weekdays:
            days = days_filter(days, day_in=self.weekdays)
        for day in days:
            day_slots1 = slots_filter(slots1, day=day)
            day_slots2 = slots_filter(slots2, day=day)
            for group in considered_groups:
                considered_courses = self.get_courses_queryset_by_parameters(ttmodel, week, group=group)
                sum1 = ttmodel.sum(ttmodel.TT[sl,c]
                                   for c in considered_courses
                                   for sl in day_slots1 & ttmodel.wdb.compatible_slots[c])
                sum2 = ttmodel.sum(ttmodel.TT[sl,c]
                                   for c in considered_courses
                                   for sl in day_slots2 & ttmodel.wdb.compatible_slots[c])
                BS1 = ttmodel.add_floor(sum1, 1, 100000)
                BS2 = ttmodel.add_floor(sum2, 1, 100000)
                both = ttmodel.add_conjunct(BS1, BS2)
                if self.weight is None:
                    ttmodel.add_constraint(both,
                                           '==',
                                           0,
                                           Constraint(constraint_type=ConstraintType.AVOID_BOTH_TIME_SAME_DAY,
                                                      groups=group, days=day, weeks=week))
                else:
                    ttmodel.add_to_group_cost(group, self.local_weight() * ponderation * both, week=week)


    def one_line_description(self):
        text = f"Pas à la fois à {french_format(self.time1)} et à {french_format(self.time2)}"
        if self.train_progs.exists():
            text += ' des promos ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        else:
            text += " de toutes les promos."
        return text


class LimitUndesiredSlotsPerWeek(TTConstraint):
    """
    Allow to limit the number of undesired slots per week
    start_time and end_time are in minuts from 0:00 AM
    """

    tutors = models.ManyToManyField('people.Tutor', blank=True, verbose_name=_('Tutors'))
    slot_start_time = models.PositiveSmallIntegerField()
    slot_end_time = models.PositiveSmallIntegerField()
    max_number = models.PositiveSmallIntegerField(validators=[MaxValueValidator(7)])

    class Meta:
        verbose_name = _('Limit undesired slots per week')
        verbose_name_plural = verbose_name

    def enrich_ttmodel(self, ttmodel, week, ponderation=1):
        tutor_to_be_considered = considered_tutors(self, ttmodel)
        days = days_filter(ttmodel.wdb.days, week=week)
        undesired_slots = [Slot(day=day, start_time=self.slot_start_time, end_time=self.slot_end_time)
                             for day in days]
        for tutor in tutor_to_be_considered:
            considered_courses = self.get_courses_queryset_by_parameters(ttmodel, week, tutor=tutor)
            expr = ttmodel.lin_expr()
            for undesired_slot in undesired_slots:
                expr += ttmodel.add_floor(
                    ttmodel.sum(ttmodel.TTinstructors[(sl, c, tutor)]
                                for c in considered_courses
                                for sl in slots_filter(ttmodel.wdb.courses_slots,
                                                       simultaneous_to=undesired_slot)
                                & ttmodel.wdb.compatible_slots[c]),
                    1,
                    len(considered_courses))
            if self.weight is None:
                ttmodel.add_constraint(expr, '<=', self.max_number,
                                       Constraint(constraint_type=ConstraintType.Undesired_slots_limit,
                                                  instructors=tutor))
            else:
                for i in range(self.max_number+1, len(days)+1):
                    cost = self.local_weight() * ponderation
                    undesired_situation = ttmodel.add_floor(expr, i, len(days))
                    ttmodel.add_to_inst_cost(tutor, cost * undesired_situation, week)
                    cost *= 2

    def one_line_description(self):
        text = ""
        if self.tutors.exists():
            text += ', '.join([tutor.username for tutor in self.tutors.all()])
        else:
            text += "Les profs"
        text += f" n'ont pas cours plus de {self.max_number} jours par semaine " \
               f"entre {french_format(self.slot_start_time)} et {french_format(self.slot_end_time)}"
        return text


class LimitSimultaneousCoursesNumber(TTConstraint):
    """
    Limit the number of simultaneous courses inside a set of courses, and/or selecting a specific course type
    and/or a set of considered modules
    """
    limit = models.PositiveSmallIntegerField()
    course_type = models.ForeignKey('base.CourseType', on_delete=models.CASCADE, null=True, blank=True)
    modules = models.ManyToManyField('base.Module',
                                     blank=True,
                                     related_name="limit_simultaneous")

    class Meta:
        verbose_name = _('Limit simultaneous courses number')
        verbose_name_plural = verbose_name

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(['course_type', "modules"])
        return attributes

    def enrich_ttmodel(self, ttmodel, week, ponderation=1):
        relevant_courses = ttmodel.wdb.courses
        if self.course_type is not None:
            relevant_courses = relevant_courses.filter(type=self.course_type)
        if self.modules.exists():
            relevant_courses = relevant_courses.filter(module__in=self.modules.all())
        nb_courses = relevant_courses.count()
        if nb_courses <= self.limit:
            return
        relevant_sum = ttmodel.lin_expr()
        if self.weight is None:
            for a_sl in ttmodel.wdb.availability_slots:
                more_than_limit = ttmodel.add_floor(
                    ttmodel.sum(ttmodel.TT[sl,c]
                                for c in relevant_courses
                                for sl in slots_filter(ttmodel.wdb.compatible_slots[c], simultaneous_to=a_sl)),
                    self.limit+1,
                    nb_courses)
                relevant_sum += more_than_limit
            ttmodel.add_constraint(relevant_sum, '==', 0,
                                   Constraint(constraint_type=ConstraintType.LimitSimultaneousCoursesNumber,
                                              weeks=week))
        else:
            for bound in range(self.limit, nb_courses+1):
                relevant_sum *= 2
                for a_sl in ttmodel.wdb.availability_slots:
                    more_than_limit = ttmodel.add_floor(
                        ttmodel.sum(ttmodel.TT[sl, c]
                                    for c in relevant_courses
                                    for sl in slots_filter(ttmodel.wdb.compatible_slots[c],
                                                           simultaneous_to=a_sl)),
                        bound + 1,
                        nb_courses)
                    relevant_sum += more_than_limit
            ttmodel.add_to_generic_cost(self.local_weight() * ponderation * relevant_sum)


    def get_viewmodel(self):
        view_model = super().get_viewmodel()
        details = view_model['details']

        details.update({'limit': self.limit,
                        'course_type': self.course_type.name if self.course_type else None,
                        'modules': ', '.join([m.abbrev for m in self.modules.all()])})

        return view_model

    def one_line_description(self):
        text = f"Parmi les cours"
        if self.course_type:
            text += f" de type {self.course_type.name}"
        if self.modules.exists():
            text += f" des modules {', '.join([m.abbrev for m in self.modules.all()])}"
        text += f" au maximum {self.limit} peuvent être simultanés."
        return text
