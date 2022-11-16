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
from TTapp.ilp_constraints.constraint_type import ConstraintType
from TTapp.ilp_constraints.constraint import Constraint
from TTapp.slots import days_filter, slots_filter
from TTapp.TTConstraints.TTConstraint import TTConstraint
from TTapp.FlopConstraint import max_weight
from django.utils.translation import gettext_lazy as _
from TTapp.TTConstraints.tutors_constraints import considered_tutors


class NotAloneForTheseCouseTypes(TTConstraint):
    '''
    TTConstraint : Guarantees that any considered tutor will not be alone to do a course of this type/module
    (and will be in parallel to one of the guide tutors)
    '''

    tutors = models.ManyToManyField('people.Tutor', blank=True, verbose_name=_('tutors'),
                                    related_name='not_alone_as_tutor')
    guide_tutors = models.ManyToManyField('people.Tutor', blank=True, verbose_name=_('guide tutors'),
                                          related_name='not_alone_as_guide')
    course_types = models.ManyToManyField('base.CourseType', blank=True)
    modules = models.ManyToManyField('base.Module', blank=True)


    class Meta:
        verbose_name = _('Not alone for those course types')
        verbose_name_plural = verbose_name

    def get_viewmodel(self):
        view_model = super().get_viewmodel()
        details = view_model['details']

        if self.tutors.exists():
            details.update({'tutors': ', '.join([tutor.username for tutor in self.tutors.all()])})

        if self.course_types.exists():
            details.update({'course_types': ', '.join([course_type.name for course_type in self.course_types.all()])})

        if self.modules.exists():
            details.update({'modules': ', '.join([module.name for module in self.modules.all()])})

        return view_model

    def one_line_description(self):
        text = "Les profs "

        if self.tutors.exists():
            text += ', '.join([tutor.username for tutor in self.tutors.all()])

        text += 'ont un prof en parallèle '

        if self.course_types.exists():
            text += ' pour les types ' +  ', '.join([course_type.name for course_type in self.course_types.all()])
        else:
            text += 'pour chaque type de cours'

        if self.modules.exists():
            text += ' dans les modules ' + ', '.join([course_type.name for course_type in self.course_types.all()])
        else:
            text += 'dans tous les modules'

        return text

    def enrich_ttmodel(self, ttmodel, week, ponderation=10):
        considered_course_types = ttmodel.wdb.course_types
        if self.course_types.exists():
            considered_course_types &= set(self.course_types.all())
        considered_modules = ttmodel.wdb.modules
        if self.modules.exists():
            considered_modules &= set(self.modules.all())
        tutors_to_consider = considered_tutors(self, ttmodel)
        guides_to_consider = set(ttmodel.wdb.instructors)
        if self.guide_tutors.exists():
            guides_to_consider &= set(self.guide_tutors.all())

        for tutor in tutors_to_consider:
            possible_tutor_guides = guides_to_consider - {tutor}
            for ct in considered_course_types:
                for m in considered_modules:
                    courses = set(ttmodel.wdb.courses.filter(module=m, type=ct, week=week))
                    tutor_courses = courses & ttmodel.wdb.possible_courses[tutor]
                    if not ttmodel.wdb.possible_courses[tutor] & courses:
                        continue
                    for sl in slots_filter(ttmodel.wdb.courses_slots, week=week):
                        tutor_sum = ttmodel.sum(ttmodel.TTinstructors[sl, c, tutor]
                                                for c in tutor_courses & ttmodel.wdb.compatible_courses[sl])
                        guide_tutors_sum = ttmodel.sum(ttmodel.TTinstructors[sl, c, g]
                                                       for g in possible_tutor_guides
                                                       for c in courses & ttmodel.wdb.compatible_courses[sl]
                                                       & ttmodel.wdb.possible_courses[g]
                                                       )
                        print(sl, tutor_sum, guide_tutors_sum)
                        if self.weight is None:
                            ttmodel.add_constraint(tutor_sum - guide_tutors_sum, '<=', 0,
                                                   Constraint(constraint_type=ConstraintType.NOT_ALONE,
                                                              instructors=tutor, weeks=week)
                                                   )
                        else:
                            tutor_without_a_guide = ttmodel.add_var()
                            # if new_var is 1, then not_ok
                            ttmodel.add_constraint(100 * tutor_without_a_guide + (guide_tutors_sum - tutor_sum),
                                                   '<=',
                                                   99)

                            # if not_ok (t_s > g_t_s) then new_var is 1
                            ttmodel.add_constraint((tutor_sum - guide_tutors_sum) - 100 * tutor_without_a_guide,
                                                   '<=',
                                                   0)
                            ttmodel.add_to_inst_cost(tutor, self.local_weight()*ponderation*tutor_without_a_guide)
