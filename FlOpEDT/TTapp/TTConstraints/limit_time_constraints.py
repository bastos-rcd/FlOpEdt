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
from TTapp.TTConstraints.TTConstraint import TTConstraint
from TTapp.slots import days_filter, slots_filter
from TTapp.ilp_constraints.constraint import Constraint
from TTapp.ilp_constraints.constraint_type import ConstraintType
from TTapp.TTConstraints.groups_constraints import considered_basic_groups
from django.utils.translation import gettext_lazy as _


def build_period_slots(ttmodel, day, period):
    if period is None:
        return slots_filter(ttmodel.wdb.courses_slots, day=day)
    else:
        return slots_filter(ttmodel.wdb.courses_slots, day=day, apm=period)


class LimitTimePerPeriod(TTConstraint):
    """
    Abstract class : Limit the number of hours (of a given course_type) in every day/half-day
    """
    course_type = models.ForeignKey('base.CourseType', on_delete=models.CASCADE, null=True, blank=True)
    max_hours = models.PositiveSmallIntegerField()
    FULL_DAY = 'fd'
    HALF_DAY = 'hd'
    PERIOD_CHOICES = ((FULL_DAY, 'Full day'), (HALF_DAY, 'Half day'))
    period = models.CharField(max_length=2, choices=PERIOD_CHOICES)

    class Meta:
        abstract = True

    def build_period_by_day(self, ttmodel, week):
        if self.period == self.FULL_DAY:
            periods = [None]
        else:
            periods = ttmodel.possible_apms

        period_by_day = []
        for day in days_filter(ttmodel.wdb.days, week=week):
            for period in periods:
                period_by_day.append((day, period,))

        return period_by_day

    def considered_train_progs(self, ttmodel):
        train_progs = self.train_progs.all()
        if not train_progs:
            train_progs = ttmodel.train_prog
        return train_progs

    def considered_courses(self, ttmodel, week, train_prog, tutor, module, group):
        return set(self.get_courses_queryset_by_parameters(ttmodel, week,
                                                           course_type=self.course_type,
                                                           train_prog=train_prog,
                                                           module=module,
                                                           group=group,
                                                           tutor=tutor))

    def build_period_expression(self, ttmodel, day, period, considered_courses, tutor=None):
        expr = ttmodel.lin_expr()
        for slot in build_period_slots(ttmodel, day, period):
            for course in considered_courses & ttmodel.wdb.compatible_courses[slot]:
                expr += ttmodel.TT[(slot, course)] * course.type.duration

        return expr

    def enrich_model_for_one_object(self, ttmodel, week, ponderation,
                                    train_prog=None, tutor=None, module=None, group=None):

        considered_courses = self.considered_courses(ttmodel, week, train_prog, tutor, module, group)
        for day, period in self.build_period_by_day(ttmodel, week):

            expr = self.build_period_expression(ttmodel, day, period, considered_courses, tutor)

            if self.weight is not None:
                var = ttmodel.add_floor(expr,
                                        int(self.max_hours * 60) + 1, 3600*24)
                ttmodel.add_to_generic_cost(self.local_weight() * ponderation * var, week=week)
            else:
                ttmodel.add_constraint(expr, '<=', self.max_hours*60,
                                       Constraint(constraint_type=ConstraintType.MAX_HOURS,
                                                  days=day, modules=module, instructors=tutor, groups=group))


class LimitGroupsTimePerPeriod(LimitTimePerPeriod):  # , pond):
    """
    Bound the number of course time (of type 'type') per day/half day for some group

    Attributes:
        groups : the groups concerned by the limitation. All the groups of self.train_progs if None.
    """
    groups = models.ManyToManyField('base.StructuralGroup',
                                    blank=True,
                                    related_name="Course_type_limits")

    class Meta:
        verbose_name = _('Limit groups busy time per period')
        verbose_name_plural = verbose_name

    def enrich_ttmodel(self, ttmodel, week, ponderation=1.):

        # if self.groups.exists():
        #     considered_groups = self.groups.filter(train_prog__in=self.considered_train_progs(ttmodel))
        # else:
        #     considered_groups = ttmodel.wdb.groups.filter(train_prog__in=self.considered_train_progs(ttmodel))
        for group in considered_basic_groups(self,ttmodel):
            self.enrich_model_for_one_object(ttmodel, week, ponderation, group=group)

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(['groups', 'course_type'])
        return attributes

    def get_viewmodel(self):
        view_model = super().get_viewmodel()
        if self.course_type is not None:
            type_value = self.course_type.name
        else:
            type_value = 'Any'

        if self.groups.exists():
            groups_value = ', '.join([group.name for group in self.groups.all()])
        else:
            groups_value = 'All'

        view_model['details'].update({
            'course_type': type_value,
            'groups': groups_value, })

        return view_model

    def one_line_description(self):
        text = "Pas plus de " + str(self.max_hours) + ' heures '
        if self.course_type is not None:
            text += 'de ' + str(self.course_type)
        text += " par "
        if self.period == self.FULL_DAY:
            text += 'jour'
        else:
            text += 'demie-journée'
        if self.groups.exists():
            text += ' pour les groupes' + ', '.join([group.name for group in self.groups.all()])
        else:
            text += " pour tous les groupes"
        if self.train_progs.exists():
            text += ' de ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        else:
            text += " de toutes les promos."
        return text


class LimitModulesTimePerPeriod(LimitTimePerPeriod):
    """
    Bound the number of hours of courses (of type 'type') per day/half day
    Attributes:
        modules : the modules concerned by the limitation. All the modules of self.train_progs if None.
    """
    modules = models.ManyToManyField('base.Module',
                                     blank=True,
                                     related_name="Course_type_limits")

    class Meta:
        verbose_name = _('Limit modules busy time per period')
        verbose_name_plural = verbose_name

    def enrich_ttmodel(self, ttmodel, week, ponderation=1.):

        if self.modules.exists():
            considered_modules = self.modules.filter(train_prog__in=self.considered_train_progs(ttmodel))
        else:
            considered_modules = ttmodel.wdb.modules.filter(train_prog__in=self.considered_train_progs(ttmodel))

        if self.train_progs.exists():
            considered_basic_groups = set(
                ttmodel.wdb.basic_groups.filter(train_prog__in=self.train_progs.all()))
        else:
            considered_basic_groups = set(ttmodel.wdb.basic_groups)

        for module in considered_modules:
            for group in considered_basic_groups:
                self.enrich_model_for_one_object(ttmodel, week, ponderation, module=module, group=group)

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(['modules', 'course_type'])
        return attributes

    def get_viewmodel(self):
        view_model = super().get_viewmodel()

        if self.course_type is not None:
            type_value = self.course_type.name
        else:
            type_value = 'Any'


        if self.modules.exists():
            module_value = ', '.join([module.abbrev for module in self.modules.all()])
        else:
            module_value = 'All'

        view_model['details'].update({
            'course_type': type_value,
            # 'tutor': tutor_value,
            'modules': module_value, })

        return view_model

    def one_line_description(self):
        text = "Pas plus de " + str(self.max_hours) + " heures"
        if self.course_type:
            text += ' de ' + str(self.course_type)
        text += " par "
        if self.period == self.FULL_DAY:
            text += 'jour'
        else:
            text += 'demie-journée'
        if self.modules.exists():
            text += " de " + ', '.join([module.abbrev for module in self.modules.all()])
        else:
            text += " de chaque module"
        if self.train_progs.exists():
            text += ' en ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        else:
            text += " dans toutes les promos."

        return text


class LimitTutorsTimePerPeriod(LimitTimePerPeriod):
    """
    Bound the time of tutor courses of type 'course_type' per day/half day for tutors
    Attributes:
        tutors : the tutors concerned by the limitation. All if None.

    """
    tutors = models.ManyToManyField('people.Tutor',
                                    blank=True,
                                    related_name="Course_type_limits")

    class Meta:
        verbose_name = _('Limit tutors busy time per period')
        verbose_name_plural = verbose_name

    def build_period_expression(self, ttmodel, day, period, considered_courses, tutor=None):
        expr = ttmodel.lin_expr()
        for slot in build_period_slots(ttmodel, day, period):
            for course in considered_courses & ttmodel.wdb.compatible_courses[slot]:
                expr += ttmodel.TTinstructors[(slot, course, tutor)] * course.type.duration

        return expr

    def enrich_ttmodel(self, ttmodel, week, ponderation=1.):

        if self.tutors.exists():
            considered_tutors = self.tutors.all()
        else:
            considered_tutors = ttmodel.wdb.instructors

        for tutor in considered_tutors:
            self.enrich_model_for_one_object(ttmodel, week, ponderation, tutor=tutor)

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(['tutors', 'course_type'])
        return attributes

    def get_viewmodel(self):
        view_model = super().get_viewmodel()

        type_value = self.course_type.name

        if self.tutors.exists():
            tutor_value = ', '.join([tutor.username for tutor in self.tutors.all()])
        else:
            tutor_value = 'All'

        view_model['details'].update({
            'course_type': type_value,
            'tutors': tutor_value,
        })

        return view_model

    def one_line_description(self):
        text = "Pas plus de " + str(self.max_hours) + " heures"
        if self.course_type:
            text += ' de ' + str(self.course_type)
        text += " par "
        if self.period == self.FULL_DAY:
            text += 'jour'
        else:
            text += 'demie-journée'
        if self.tutors.exists():
            text += ' pour ' + ', '.join([tutor.username for tutor in self.tutors.all()])
        else:
            text += " pour tous les profs "
        if self.train_progs.exists():
            text += ' en ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        return text


class LimitCourseTypeTimePerPeriod(LimitTimePerPeriod):  # , pond):
    """
    Bound the number of course time (of type 'type') per day/half day
    """


    def enrich_ttmodel(self, ttmodel, week, ponderation=1.):
        self.enrich_model_for_one_object(ttmodel, week, ponderation)

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(['course_type'])
        return attributes

    def get_viewmodel(self):
        view_model = super().get_viewmodel()
        if self.course_type is not None:
            type_value = self.course_type.name
        else:
            type_value = 'Any'

        view_model['details'].update({
            'course_type': type_value})

        return view_model

    def one_line_description(self):
        text = "Pas plus de " + str(self.max_hours) + ' heures '
        if self.course_type is not None:
            text += 'de ' + str(self.course_type)
        text += " par "
        if self.period == self.FULL_DAY:
            text += 'jour'
        else:
            text += 'demie-journée'
        if self.train_progs.exists():
            text += ' pour ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        else:
            text += " pour toutes les promos."
        return text