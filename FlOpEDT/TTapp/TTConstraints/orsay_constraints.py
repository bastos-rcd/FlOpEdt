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


from django.contrib.postgres.fields import ArrayField
from base.timing import Day, TimeInterval, flopdate_to_datetime
import datetime as dt
from base.partition import Partition
from base.models import SchedulingPeriod
from people.models import Tutor

from django.db import models
from django.db.models import Q


from django.core.exceptions import ObjectDoesNotExist

from base.timing import french_format
from base.timing import Day

from TTapp.ilp_constraints.constraint_type import ConstraintType
from TTapp.ilp_constraints.constraint import Constraint
from TTapp.slots import days_filter, slots_filter
from TTapp.TTConstraints.TTConstraint import TTConstraint
from TTapp.TTConstraints.groups_constraints import considered_basic_groups
from TTapp.slots import Slot
from TTapp.TTConstraints.tutors_constraints import considered_tutors
from django.utils.translation import gettext_lazy as _


class GroupsLunchBreak(TTConstraint):
    """
    Ensures time for lunch in a given interval for given groups (all if groups is Null)
    """
    train_progs = models.ManyToManyField('base.TrainingProgramme',
                                         blank=True)
    start_lunch_time = models.TimeField()
    end_lunch_time = models.TimeField()
    # ArrayField unusable with django-import-export
    weekdays = ArrayField(models.CharField(max_length=2, choices=Day.CHOICES), blank=True, null=True)
    lunch_length = models.DurationField() 
    groups = models.ManyToManyField('base.StructuralGroup', blank=True, related_name='lunch_breaks_constraints')

    class Meta:
        verbose_name = _('Lunch break for groups')
        verbose_name_plural = verbose_name

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(['train_progs', 'groups'])
        return attributes

    def enrich_ttmodel(self, ttmodel, period, ponderation=100):
        considered_groups = considered_basic_groups(self, ttmodel)
        days = days_filter(ttmodel.wdb.days, period=period)
        if self.weekdays:
            days = days_filter(days, weekday_in=self.weekdays)
        for day in days:
            day_lunch_start_time = dt.datetime.combine(day, self.start_lunch_time)
            local_slots = []
            slot_start_time = day_lunch_start_time
            slot_end_time = slot_start_time + self.lunch_length 
            while slot_end_time <= dt.datetime.combine(day, self.end_lunch_time):
                local_slots.append(Slot(slot_start_time, slot_end_time))
                slot_start_time += dt.timedelta(minutes=15)
                slot_end_time += dt.timedelta(minutes=15)
            slots_nb = len(local_slots)
            # pour chaque groupe, au moins un de ces slots ne voit aucun cours lui être simultané
            slot_vars = {}

            for group in considered_groups:
                considered_courses = self.get_courses_queryset_by_parameters(ttmodel, period, group=group)
                for local_slot in local_slots:
                    # Je veux que slot_vars[group, local_slot] soit à 1
                    # si et seulement si undesired_scheduled_courses vaut plus que 1
                    undesired_scheduled_courses = \
                        ttmodel.sum(ttmodel.TT[sl, c] for c in considered_courses
                                    for sl in slots_filter(ttmodel.wdb.compatible_slots[c],
                                                           simultaneous_to=local_slot))
                    slot_vars[group, local_slot] = ttmodel.add_floor(expr=undesired_scheduled_courses,
                                                                     floor=1,
                                                                     bound=len(considered_courses))
                not_ok = ttmodel.add_floor(expr=ttmodel.sum(slot_vars[group, sl] for sl in local_slots),
                                           floor=slots_nb,
                                           bound=2 * slots_nb)

                if self.weight is None:
                    ttmodel.add_constraint(not_ok,'==', 0, Constraint(ConstraintType.LUNCH_BREAK,
                                                                      groups=group))
                    # ttmodel.add_constraint(ttmodel.sum(slot_vars[group, sl] for sl in local_slots),
                    #                        '<=', len(local_slots),
                    #                        Constraint(constraint_type=ConstraintType.LUNCH_BREAK,
                    #                                   groups=group, days=day))
                else:
                    cost = not_ok * ponderation * self.local_weight()
                    # cost = ttmodel.sum(slot_vars[group, sl] for sl in local_slots) * ponderation \
                    #        * self.local_weight()
                    ttmodel.add_to_group_cost(group, cost, period)


    def one_line_description(self):
        text = f"Il faut une pause déjeuner d'au moins {self.lunch_length} minutes " \
               f"entre {french_format(self.start_lunch_time)} et {french_format(self.end_lunch_time)}"
        try:
            text += " les " + ', '.join([wd for wd in self.weekdays])
        except ObjectDoesNotExist:
            pass
        if self.groups.exists():
            text += ' pour les groupes ' + ', '.join([group.name for group in self.groups.all()])
        else:
            text += " pour tous les groupes"

        if self.train_progs.exists():
            text += ' de ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        else:
            text += " de toutes les promos."
        return text
    
    def complete_group_partition(self, partition, group, period):
        """
            Complete the partition in parameters with informations given by this GroupLunchBreak constraint if it
        concern the given group and period.
        This method is called by functions in partition_with_constraints.py to initialize a partition used in pre_analyse methods.

        :param partition: A partition (empty or not) with informations about a group's availability.
        :type partition: Partition
        :param tutor: The group from whom the partition is about.
        :type tutor: StructuralGroup
        :param period: The SchedulingPeriod we want to make a pre-analysis on (can be None if all).
        :type week: SchedulingPeriod
        :return: A partition with new informations if the given tutor is concerned by this GroupLunchBreak constraint.
        :rtype: Partition

        """

        if (not self.groups.exists() or group in self.groups.all()) \
                and (not self.periods.exists() or period in self.periods.all()):
            days = period.dates()
            if self.weekdays:
                days = days_filter(days, day_in=self.weekdays)
            for day in days :
                max_lunch_start_time = dt.datetime.combine(day, self.end_lunch_time) - self.lunch_length
                partition.add_slot(TimeInterval(max_lunch_start_time, #dt.datetime.combine(day, self.start_lunch_time),                                                
                                                dt.datetime.combine(day, self.end_lunch_time)),
                                   "forbidden",
                                   {"value": 0, "forbidden": True, "group_lunch_break": group.name}
                                   )

        return partition


class TutorsLunchBreak(TTConstraint):
    """
    Ensures time for lunch in a given interval for given tutors (all if tutors is Null)
    """
    start_lunch_time = models.TimeField(help_text=_('start lunch time'))
    end_lunch_time = models.TimeField(help_text=_('end lunch time')) 
    weekdays = ArrayField(models.CharField(max_length=2, choices=Day.CHOICES), blank=True, null=True,
                          help_text=_('considered week days'))
    lunch_length = models.DurationField(help_text=_('minimal lunch length'))  
    tutors = models.ManyToManyField('people.Tutor', blank=True, related_name='lunch_breaks_constraints',
                                    help_text=_('considered tutors'))

    class Meta:
        verbose_name = _('Lunch break for tutors')
        verbose_name_plural = verbose_name

    def enrich_ttmodel(self, ttmodel, period, ponderation=100):
        tutors_to_be_considered = considered_tutors(self, ttmodel)
        if self.tutors.exists():
            tutors_to_be_considered &= set(self.tutors.all())
        days = days_filter(ttmodel.wdb.days, period=period)
        if self.weekdays:
            days = days_filter(days, weekday_in=self.weekdays)
        for day in days:
            day_lunch_start_time = dt.datetime.combine(day, self.start_lunch_time)
            local_slots = []
            slot_start_time = day_lunch_start_time
            slot_end_time = slot_start_time + self.lunch_length 
            while slot_end_time <= dt.datetime.combine(day, self.end_lunch_time):
                local_slots.append(Slot(slot_start_time, slot_end_time))
                slot_start_time += dt.timedelta(minutes=15)
                slot_end_time += dt.timedelta(minutes=15)
            slots_nb = len(local_slots)
            # pour chaque prof, au moins un de ces slots ne voit aucun cours lui être simultané
            for tutor in tutors_to_be_considered:
                slot_vars = {}
                other_deps_unavailable_slots_number = 0
                considered_courses = self.get_courses_queryset_by_parameters(ttmodel, period, tutor=tutor)
                if not considered_courses:
                    continue
                other_dep_scheduled_courses = \
                    set(ttmodel.wdb.other_departments_scheduled_courses_for_tutor[tutor]) | \
                    set(ttmodel.wdb.other_departments_scheduled_courses_for_supp_tutor[tutor])
                for local_slot in local_slots:
                    # Je veux que slot_vars[tutor, local_slot] soit à 1
                    # si et seulement si
                    # undesired_scheduled_courses ou other_dep_undesired_sc_nb vaut plus que 1
                    considered_sl_c = set((sl,c) for c in considered_courses
                                          for sl in slots_filter(ttmodel.wdb.compatible_slots[c],
                                                                 simultaneous_to=local_slot))
                    if not considered_sl_c:
                        continue
                    undesired_scheduled_courses = \
                        ttmodel.sum(ttmodel.TTinstructors[sl, c, tutor]
                                    for (sl,c) in considered_sl_c)
                    if not other_dep_scheduled_courses:
                        other_dep_undesired_sc_nb = 0
                    else:
                        other_dep_undesired_scheduled_courses = \
                            set(sc for sc in other_dep_scheduled_courses
                                if (sc.start_time < local_slot.end_time
                                    and local_slot.start_time < sc.end_time))
                        other_dep_undesired_sc_nb = len(other_dep_undesired_scheduled_courses)
                        if other_dep_undesired_sc_nb:
                            other_deps_unavailable_slots_number += 1
                    undesired_expression = undesired_scheduled_courses + other_dep_undesired_sc_nb * ttmodel.one_var
                    slot_vars[local_slot] = ttmodel.add_floor(expr=undesired_expression,
                                                              floor=1,
                                                              bound=len(considered_courses))
                if not slot_vars:
                    continue

                if other_deps_unavailable_slots_number == slots_nb:
                    ttmodel.add_warning(tutor, _(f"Not able to eat in other departments on {day}-{period}"))
                    continue
                not_ok = ttmodel.add_floor(expr=ttmodel.sum(slot_vars[sl] for sl in slot_vars),
                                           floor=slots_nb,
                                           bound=2 * slots_nb)

                if self.weight is None:
                    ttmodel.add_constraint(not_ok,'==', 0, Constraint(ConstraintType.LUNCH_BREAK,
                                                                      instructors=tutor))
                    # ttmodel.add_constraint(ttmodel.sum(slot_vars[group, sl] for sl in local_slots),
                    #                        '<=', len(local_slots),
                    #                        Constraint(constraint_type=ConstraintType.LUNCH_BREAK,
                    #                                   groups=group, days=day))
                else:
                    cost = not_ok * ponderation * self.local_weight()
                    # cost = ttmodel.sum(slot_vars[group, sl] for sl in local_slots) * ponderation \
                    #        * self.local_weight()
                    ttmodel.add_to_inst_cost(tutor, cost, period)
                    
    def complete_tutor_partition(self, partition, tutor, period):
        """
                Complete the partition in parameters with informations given by this TutorsLunchBreak constraint if it
            concern the given tutor and period.
            This method is called by functions in partition_with_constraints.py to initialize a partition used in pre_analyse methods.

            :param partition: A partition (empty or not) with informations about a tutor's availability.
            :type partition: Partition
            :param tutor: The tutor from whom the partition is about.
            :type tutor: Tutor
            :param period: The SchedulingPeriod we want to make a pre-analysis on (can be None if all).
            :type period: SchedulingPeriod
            :return: A partition with new informations if the given tutor is concerned by this TutorsLunchBreak constraint.
            :rtype: Partition

        """

        if (not self.tutors.exists() or tutor in self.tutors.all()) \
                and (not self.periods.exists() or period in self.periods.all()):
            days = period.dates()
            if self.weekdays:
                days = days_filter(days, day_in=self.weekdays)
            for day in days :
                max_lunch_start_time = dt.datetime.combine(day, self.end_lunch_time) - self.lunch_length
                partition.add_slot(TimeInterval(max_lunch_start_time, #dt.datetime.combine(day, self.start_lunch_time),
                                                dt.datetime.combine(day, self.end_lunch_time)),
                                   "forbidden",
                                   {"value": 0, "forbidden": True, "tutor_lunch_break": tutor.username}
                                   )

        return partition


    def one_line_description(self):
        text = f"Il faut une pause déjeuner d'au moins {self.lunch_length} minutes " \
               f"entre {french_format(self.start_lunch_time)} et {french_format(self.end_lunch_time)}"
        try:
            text += " les " + ', '.join([wd for wd in self.weekdays])
        except ObjectDoesNotExist:
            pass
        if self.tutors.exists():
            text += ' pour ' + ', '.join([tutor.username for tutor in self.tutors.all()])
        else:
            text += " pour tous les profs."
        return text


class BreakAroundCourseType(TTConstraint):
    """
    Ensures that the courses of a given course type and other types of courses cannot be consecutive for the given groups.
    """
    weekdays = ArrayField(models.CharField(max_length=2, choices=Day.CHOICES), blank=True, null=True)
    groups = models.ManyToManyField('base.StructuralGroup', blank=True, related_name='amphi_break_constraint')
    course_type = models.ForeignKey('base.CourseType', related_name='amphi_break_constraint', on_delete=models.CASCADE)
    min_break_length = models.DurationField(default=dt.timedelta(minutes=15))

    class Meta:
        verbose_name = _('A break around some type courses')
        verbose_name_plural = verbose_name

    def enrich_ttmodel(self, ttmodel, period, ponderation=1000):
        considered_groups = considered_basic_groups(self, ttmodel)
        days = days_filter(ttmodel.wdb.days, period=period)
        if self.weekdays:
            days = days_filter(days, day_in=self.weekdays)
        for group in considered_groups:
            specific_courses = set(self.get_courses_queryset_by_parameters(ttmodel, period, group=group, course_type=self.course_type))
            other_courses = set(self.get_courses_queryset_by_parameters(ttmodel, period, group=group).exclude(type=self.course_type))
            broken_breaks = ttmodel.lin_expr()
            for day in days:
                day_slots = slots_filter(ttmodel.wdb.courses_slots, day=day)
                for slot1 in day_slots:
                    successive_slots = set(sl for sl in day_slots
                                           if slot1.end_time <= sl.start_time < slot1.end_time + self.min_break_length)
                    if not successive_slots:
                        continue
                    amphi_slot1 = ttmodel.sum(ttmodel.TT[slot1, c] for c in specific_courses & ttmodel.wdb.compatible_courses[slot1])
                    other_slot1 = ttmodel.sum(ttmodel.TT[slot1, c] for c in other_courses & ttmodel.wdb.compatible_courses[slot1])
                    other_slot2 = ttmodel.sum(ttmodel.TT[slot2, c]
                                              for slot2 in successive_slots
                                              for c in other_courses & ttmodel.wdb.compatible_courses[slot2])
                    amphi_slot2 = ttmodel.sum(ttmodel.TT[slot2, c]
                                              for slot2 in successive_slots
                                              for c in specific_courses & ttmodel.wdb.compatible_courses[slot2])
                    a1o2 = ttmodel.add_floor(expr=amphi_slot1+other_slot2, floor=2, bound=2)
                    o1a2 = ttmodel.add_floor(expr=amphi_slot2+other_slot1, floor=2, bound=2)
                    broken_breaks += a1o2 + o1a2

            if self.weight is None:
                ttmodel.add_constraint(broken_breaks, '==', 0,
                                       Constraint(constraint_type=ConstraintType.BREAK_AROUND_COURSE,
                                                  groups=group))
            else:
                cost = broken_breaks * ponderation * self.local_weight()
                ttmodel.add_to_group_cost(group, cost, period)


    def one_line_description(self):
        text = f"Il faut une pause " \
               f"entre un cours de type {self.course_type.name} et un autre type de cours"
        try:
            text += " les " + ', '.join([wd for wd in self.weekdays])
        except ObjectDoesNotExist:
            pass
        if self.groups.exists():
            text += ' pour les groupes ' + ', '.join([group.name for group in self.groups.all()])
        else:
            text += " pour tous les groupes"

        if self.train_progs.exists():
            text += ' de ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        else:
            text += " de toutes les promos."
        return text
