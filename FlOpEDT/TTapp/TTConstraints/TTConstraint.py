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

from core.decorators import timer

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
    def enrich_ttmodel(self, ttmodel, week, ponderation=1):
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

    def get_courses_queryset_by_parameters(self, ttmodel, week,
                                           train_progs=None,
                                           train_prog=None,
                                           module=None,
                                           group=None,
                                           course_type=None,
                                           room_type=None,
                                           tutor=None):
        courses_qs = FlopConstraint.get_courses_queryset_by_parameters(self, ttmodel, week,
                                                                       train_progs=train_progs,
                                                                       train_prog=train_prog,
                                                                       module=module,
                                                                       group=group,
                                                                       course_type=course_type,
                                                                       room_type=room_type)

        #if tutor is not None, we have to reduce to the courses that are in possible_course[tutor]
        if tutor is not None:
            if tutor in ttmodel.wdb.instructors:
                return courses_qs.filter(id__in = [c.id for c in ttmodel.wdb.possible_courses[tutor]])
            else:
                return courses_qs.filter(id__in = [])
        return courses_qs

    def get_courses_queryset_by_attributes(self, ttmodel, week, **kwargs):
        """
        Filter courses depending constraint attributes
        """
        if self.train_progs.exists() and 'train_progs' not in kwargs:
            kwargs['train_progs'] = self.train_progs.all()
        return FlopConstraint.get_courses_queryset_by_attributes(self, ttmodel, week, **kwargs)