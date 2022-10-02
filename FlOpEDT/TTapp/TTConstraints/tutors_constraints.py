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

from django.db import models

from TTapp.helpers.minhalfdays import MinHalfDaysHelperTutor

from TTapp.ilp_constraints.constraint_type import ConstraintType
from TTapp.ilp_constraints.constraint import Constraint
from TTapp.slots import days_filter, slots_filter
from TTapp.TTConstraints.TTConstraint import TTConstraint
from TTapp.FlopConstraint import max_weight
from django.utils.translation import gettext_lazy as _


def considered_tutors(tutors_ttconstraint, ttmodel):
    tutors_to_consider = set(ttmodel.wdb.instructors)
    if tutors_ttconstraint.tutors.exists():
        tutors_to_consider &= set(tutors_ttconstraint.tutors.all())
    return tutors_to_consider


class MinTutorsHalfDays(TTConstraint):
    """
    All courses will fit in a minimum of half days
    Optional: if 2 courses only, possibility to join it
    """
    tutors = models.ManyToManyField('people.Tutor', blank=True, verbose_name=_('tutors'))
    join2courses = models.BooleanField(
        verbose_name='If a tutor has 2 or 4 courses only, join it?',
        default=False)

    class Meta:
        verbose_name = _('Minimize busy half days for tutors')
        verbose_name_plural = verbose_name

    def enrich_ttmodel(self, ttmodel, week, ponderation=5):

        helper = MinHalfDaysHelperTutor(ttmodel, self, week, ponderation)
        for tutor in considered_tutors(self, ttmodel):
            helper.enrich_model(tutor=tutor)

    def get_viewmodel(self):
        view_model = super().get_viewmodel()
        details = view_model['details']

        if self.tutors.exists():
            details.update({'tutors': ', '.join([tutor.username for tutor in self.tutors.all()])})

        return view_model

    def one_line_description(self):
        text = "Minimise les demie-journées"

        if self.tutors.exists():
            text += ' de : ' + ', '.join([tutor.username for tutor in self.tutors.all()])
        else:
            text += " de tous les profs"

        if self.train_progs.exists():
            text += ' en ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])

        return text


class MinNonPreferedTutorsSlot(TTConstraint):
    """
    Minimize the use of unprefered Slots for tutors
    """
    tutors = models.ManyToManyField('people.Tutor', blank=True,
                                    related_name='min_non_prefered_tutors_slots_constraints')

    class Meta:
        verbose_name = _('Minimize undesired slots for tutors')
        verbose_name_plural = verbose_name

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(['tutors'])
        return attributes

    def enrich_ttmodel(self, ttmodel, week, ponderation=None):
        if ponderation is None:
            ponderation = ttmodel.min_ups_i
        tutors = considered_tutors(self, ttmodel)
        for sl in ttmodel.wdb.availability_slots:
            for tutor in tutors:
                filtered_courses = set(c for c in ttmodel.wdb.possible_courses[tutor] if c.week == week)
                for c in filtered_courses:
                    slot_vars_sum = ttmodel.sum(ttmodel.TTinstructors[(sl2, c, tutor)]
                                                for sl2 in slots_filter(ttmodel.wdb.compatible_slots[c],
                                                                        simultaneous_to=sl))
                    cost = (float(self.local_weight()) / max_weight) \
                        * ponderation * slot_vars_sum \
                        * ttmodel.unp_slot_cost[tutor][sl]
                    ttmodel.add_to_inst_cost(tutor, cost, week=week)

    def one_line_description(self):
        text = "Respecte les préférences"
        if self.tutors.exists():
            text += ' de ' + ', '.join([tutor.username for tutor in self.tutors.all()])
        else:
            text += ' de tous les profs.'
        return text


class MinimizeBusyDays(TTConstraint):
    """
    This class is a template for writing your own custom contraint.

    The module can contains several custom constraints.
    """
    tutors = models.ManyToManyField('people.Tutor', blank=True)

    class Meta:
        verbose_name = _('Minimize tutors busy days')
        verbose_name_plural = verbose_name

    def enrich_ttmodel(self, ttmodel, week, ponderation=None):
        """
        Minimize the number of busy days for tutor with cost
        (if it does not overcome the bound expressed in pref_hours_per_day)
        """
        if ponderation is None:
            ponderation = ttmodel.min_bd_i

        tutors = considered_tutors(self, ttmodel)

        for tutor in tutors:
            slot_by_day_cost = ttmodel.lin_expr()
            # need to be sorted
            courses_hours = sum(c.type.duration
                                for c in (ttmodel.wdb.courses_for_tutor[tutor]
                                          | ttmodel.wdb.courses_for_supp_tutor[tutor])
                                & ttmodel.wdb.courses_by_week[week]) / 60
            nb_days = len(days_filter(ttmodel.wdb.days, week=week))
            minimal_number_of_days = nb_days
            # for any number of days inferior to nb_days
            for d in range(nb_days, 0, -1):
                # if courses fit in d-1 days
                if courses_hours <= tutor.preferences.pref_hours_per_day * (d-1):
                    # multiply the previous cost by 2
                    slot_by_day_cost *= 2
                    # add a cost for having d busy days
                    slot_by_day_cost += ttmodel.IBD_GTE[week][d][tutor]
                else:
                    minimal_number_of_days = d
                    break
            if self.weight is None:
                if minimal_number_of_days < nb_days:
                    ttmodel.add_constraint(ttmodel.IBD_GTE[week][minimal_number_of_days + 1][tutor], '==', 0,
                                           Constraint(constraint_type=ConstraintType.MinimizeBusyDays,
                                                      instructors=tutor, weeks=week))
            else:
                ttmodel.add_to_inst_cost(tutor, self.local_weight() * ponderation * slot_by_day_cost, week=week)

    def get_viewmodel(self):
        view_model = super().get_viewmodel()
        details = view_model['details']

        if self.tutors.exists():
            details.update({'tutors': ', '.join([tutor.username for tutor in self.tutors.all()])})
        else:
            details.update({'tutors': 'All'})

        return view_model

    def one_line_description(self):
        """
        You can give a contextual explanation about what this constraint doesnt
        """
        return "MinimizeBusyDays online description"


class RespectMaxHoursPerDay(TTConstraint):
    """
    Respect the max_hours_per_day declared
    """
    tutors = models.ManyToManyField('people.Tutor', blank=True)

    class Meta:
        verbose_name = _('Respect max hours per days bounds')
        verbose_name_plural = verbose_name

    def enrich_ttmodel(self, ttmodel, week, ponderation=1):
        """
        Minimize the number of busy days for tutor with cost
        (if it does not overcome the bound expressed in pref_hours_per_day)
        """
        tutors = considered_tutors(self, ttmodel)

        for tutor in tutors:
            for d in days_filter(ttmodel.wdb.days, week=week):
                other_departments_hours_nb = sum(sc.course.type.duration
                                                 for sc in ttmodel.wdb.other_departments_scheduled_courses_for_tutor[tutor]
                                                 if sc.course.week == week and sc.day == d.day) / 60
                max_hours_nb = max(tutor.preferences.max_hours_per_day - other_departments_hours_nb, 0)
                if self.weight is None:
                    ttmodel.add_constraint(tutor_teaching_time_by_day_expression(ttmodel, tutor, d),
                                           '<=',
                                           max_hours_nb,
                                           Constraint(constraint_type=ConstraintType.MAX_HOURS_PER_DAY,
                                                      instructors=tutor,
                                                      days=d))
                else:
                    undesired_situation = ttmodel.add_floor(tutor_teaching_time_by_day_expression(ttmodel, tutor, d),
                                                            max_hours_nb,
                                                            100000)
                    ttmodel.add_to_inst_cost(tutor, self.local_weight() * ponderation * undesired_situation,
                                             week=week)

    def get_viewmodel(self):
        view_model = super().get_viewmodel()
        details = view_model['details']

        if self.tutors.exists():
            details.update({'tutors': ', '.join([tutor.username for tutor in self.tutors.all()])})
        else:
            details.update({'tutors': 'All'})
        return view_model

    def one_line_description(self):
        """
        You can give a contextual explanation about what this constraint doesnt
        """
        return "Respect max hours per day"


class RespectMinHoursPerDay(TTConstraint):
    """
    Respect the min_hours_per_day declared
    """
    tutors = models.ManyToManyField('people.Tutor', blank=True)

    class Meta:
        verbose_name = _('Respect min hours per day bounds')
        verbose_name_plural = verbose_name

    def enrich_ttmodel(self, ttmodel, week, ponderation=1):
        """
        avoid situations in which a teaching day has less hours than min declared
        """
        tutors = considered_tutors(self, ttmodel)

        for tutor in tutors:
            for d in days_filter(ttmodel.wdb.days, week=week):
                other_departments_hours_nb = sum(sc.course.type.duration
                                                 for sc in ttmodel.wdb.other_departments_scheduled_courses_for_tutor[tutor]
                                                 if sc.course.week == week and sc.day == d.day) / 60
                min_hours_nb = max(tutor.preferences.min_hours_per_day - other_departments_hours_nb, 0)
                if min_hours_nb == 0:
                    continue
                has_enough_time = ttmodel.add_floor(tutor_teaching_time_by_day_expression(ttmodel, tutor, d),
                                                    min_hours_nb,
                                                    100000)
                undesired_situation = ttmodel.IBD[(tutor, d)] - has_enough_time
                if self.weight is None:
                    ttmodel.add_constraint(undesired_situation,
                                           '==',
                                           0,
                                           Constraint(constraint_type=ConstraintType.MIN_HOURS_PER_DAY,
                                                      instructors=tutor,
                                                      days=d))
                else:
                    ttmodel.add_to_inst_cost(tutor, self.local_weight() * ponderation * undesired_situation,
                                             week=week)

    def get_viewmodel(self):
        view_model = super().get_viewmodel()
        details = view_model['details']

        if self.tutors.exists():
            details.update({'tutors': ', '.join([tutor.username for tutor in self.tutors.all()])})
        else:
            details.update({'tutors': 'All'})
        return view_model

    def one_line_description(self):
        """
        You can give a contextual explanation about what this constraint doesnt
        """
        return "Respect min hours per day"


class LowerBoundBusyDays(TTConstraint):
    """
    Impose a minimum number of days if the number of hours is higher than a lower bound
    """
    tutor = models.ForeignKey('people.Tutor', on_delete=models.CASCADE)
    min_days_nb = models.PositiveSmallIntegerField()
    lower_bound_hours = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name = _('Lower bound tutor busy days')
        verbose_name_plural = verbose_name

    def enrich_ttmodel(self, ttmodel, week, ponderation=1):
        relevant_courses = self.get_courses_queryset_by_attributes(ttmodel, week)

        if sum(c.type.duration for c in relevant_courses) > self.lower_bound_hours:
            ttmodel.add_constraint(ttmodel.IBD_GTE[self.min_days_nb][self.tutor], '==', 1,
                                   Constraint(constraint_type=ConstraintType.LowerBoundBusyDays, instructors=self.tutor))

    def one_line_description(self):
        return f"Si plus de {self.lower_bound_hours} heures pour {self.tutor}  alors au moins {self.min_days_nb} jours"

    def get_viewmodel(self):
        view_model = super().get_viewmodel()

        view_model['details'].update({
            'tutor': self.tutor.username,
        })

        return view_model


def tutor_teaching_time_by_day_expression(ttmodel, tutor, day):
    return ttmodel.sum(ttmodel.TTinstructors[sl, c, tutor] * sl.duration / 60
                       for c in ttmodel.wdb.possible_courses[tutor]
                       for sl in slots_filter(ttmodel.wdb.compatible_slots[c], day=day)) \
           + ttmodel.sum(ttmodel.TT[sl, c] * sl.duration / 60
                         for c in ttmodel.wdb.courses_for_supp_tutor[tutor]
                         for sl in slots_filter(ttmodel.wdb.compatible_slots[c], day=day))