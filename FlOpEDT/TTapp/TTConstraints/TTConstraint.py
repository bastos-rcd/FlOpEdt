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

from base.models import TimeGeneralSettings
from django.core.validators import MinValueValidator, MaxValueValidator

from django.utils.translation import gettext_lazy as _

from django.db import models

from FlOpEDT.decorators import timer

from TTapp.FlopConstraint import FlopConstraint


class TTConstraint(FlopConstraint):
    """
    Abstract parent class of specific constraints that users may define

    Attributes:
        department : the department concerned by the constraint. Has to be filled.
        train_progs : the training programs concerned by the constraint. All of self.department if None
        weeks : the weeks for which the constraint should be applied. All if None.
        weight : from 1 to max_weight if the constraint is optional, depending on its importance
                 None if the constraint is necessary
        is_active : usefull to de-activate a Constraint just before the generation
    """
    train_progs = models.ManyToManyField('base.TrainingProgramme',
                                         blank=True)

    class Meta:
        abstract = True

    @timer
    def enrich_model(self, ttmodel, week, ponderation=1):
        raise NotImplementedError

    def get_viewmodel(self):
        """
        :return: a dictionnary with view-related data
        """
        result = FlopConstraint.get_viewmodel(self)
        if self.train_progs.exists():
            train_prog_value = ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        else:
            train_prog_value = 'All'

        result['train_progs'] = train_prog_value

        return result

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        return ['train_progs', 'department',]

    @staticmethod
    def get_courses_queryset_by_parameters(ttmodel, week,
                                           train_progs=None,
                                           train_prog=None,
                                           module=None,
                                           group=None,
                                           course_type=None,
                                           room_type=None,
                                           tutor=None):
        """
        Filter courses depending on constraints parameters
        :parameter group : if not None, return all courses that has one group connected to group
        """
        courses_qs = ttmodel.wdb.courses.filter(week=week)
        courses_filter = {}

        if train_progs is not None:
            courses_filter['module__train_prog__in'] = train_progs

        if train_prog is not None:
            courses_filter['module__train_prog'] = train_prog

        if module is not None:
            courses_filter['module'] = module

        if group is not None:
            courses_filter['groups__in'] = group.connected_groups()

        if course_type is not None:
            courses_filter['type'] = course_type

        if room_type is not None:
            courses_filter['room_type'] = room_type

        if tutor is not None:
            if tutor in ttmodel.wdb.instructors:
                courses_filter['id__in'] = [c.id for c in ttmodel.wdb.possible_courses[tutor]]
            else:
                courses_filter['id__in'] = []

        return courses_qs.filter(**courses_filter)

    def get_courses_queryset_by_attributes(self, ttmodel, week, **kwargs):
        """
        Filter courses depending constraint attributes
        """
        if self.train_progs.exists() and 'train_progs' not in kwargs:
            kwargs['train_progs'] = self.train_progs.all()
        for attr in ['train_prog', 'module', 'group', 'course_type', 'tutor', 'room_type']:
            if hasattr(self, attr) and attr not in kwargs:
                kwargs[attr] = getattr(self, attr)
        return self.get_courses_queryset_by_parameters(ttmodel, week, **kwargs)