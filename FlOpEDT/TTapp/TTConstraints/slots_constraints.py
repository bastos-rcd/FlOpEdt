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

from django.db import models

from base.timing import french_format

from TTapp.ilp_constraints.constraint_type import ConstraintType
from TTapp.ilp_constraints.constraint import Constraint
from TTapp.slots import days_filter, slots_filter
from base.timing import Day
from TTapp.TTConstraint import TTConstraint
from TTapp.ilp_constraints.constraints.dependencyConstraint import DependencyConstraint


class SimultaneousCourses(TTConstraint):
    """
    Force courses to start simultaneously
    """
    courses = models.ManyToManyField('base.Course', related_name='simultaneous_courses_constraints')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        courses_weeks_and_years = set((c.week, c.year) for c in self.courses.all())
        nb = len(courses_weeks_and_years)
        if nb == 0:
            return
        elif nb > 1:
            self.delete()
            raise Exception("Simultaneous courses need to have the same week: not saved")
        else:
            week, year = courses_weeks_and_years.pop()
            self.week = week
            self.year = year
            super().save(*args, **kwargs)

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(['courses'])
        return attributes

    def enrich_model(self, ttmodel, week, ponderation=1):
        course_types = set(c.type for c in self.courses.all())
        relevant_courses = list(c for c in self.courses.all() if c.week in ttmodel.weeks)
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
        verbose_name_plural = "Simultaneous courses"


class LimitedStartTimeChoices(TTConstraint):
    """
    Limit the possible start times
    """

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
    group = models.ForeignKey('base.Group',
                              null=True,
                              blank=True,
                              default=None,
                              on_delete=models.CASCADE)
    course_type = models.ForeignKey('base.CourseType',
                                    null=True,
                                    blank=True,
                                    default=None,
                                    on_delete=models.CASCADE)
    possible_week_days = ArrayField(models.CharField(max_length=2, choices=Day.CHOICES), blank=True, null=True)
    possible_start_times = ArrayField(models.PositiveSmallIntegerField())

    def enrich_model(self, ttmodel, week, ponderation=1.):
        fc = self.get_courses_queryset_by_attributes(ttmodel, week)
        pst = self.possible_start_times
        if self.possible_week_days is None:
            pwd = list(c[0] for c in Day.CHOICES)
        else:
            pwd = self.possible_week_days
        if self.tutor is None:
            relevant_sum = ttmodel.sum(ttmodel.TT[(sl, c)]
                                       for c in fc
                                       for sl in ttmodel.wdb.compatible_slots[c] if (sl.start_time not in pst or
                                                                                     sl.day.day not in pwd))
        else:
            relevant_sum = ttmodel.sum(ttmodel.TTinstructors[(sl, c, self.tutor)]
                                       for c in fc
                                       for sl in ttmodel.wdb.compatible_slots[c] if (sl.start_time not in pst or
                                                                                     sl.day.day not in pwd))
        if self.weight is not None:
            ttmodel.add_to_generic_cost(self.local_weight() * ponderation * relevant_sum, week=week)
        else:
            ttmodel.add_constraint(relevant_sum, '==', 0,
                                   Constraint(constraint_type=ConstraintType.LIMITED_START_TIME_CHOICES,
                                              instructors=self.tutor, groups=self.group, modules=self.module,))

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
            text += " pour toutes les promos."
        if self.group:
            text += ' avec le groupe ' + str(self.group)
        text += " ne peuvent avoir lieu qu'à "
        for pst in self.possible_start_times:
            text += french_format(pst) + ', '
        return text



class ConsiderDepencies(TTConstraint):
    """
    Transform the constraints of dependency saved on the DB in model constraints:
    -include dependencies and successiveness
    -include non same-day constraint
    -include simultaneity (double dependency)
    If there is a weight, it's a preference, else it's a constraint...
    """
    modules = models.ManyToManyField('base.Module', blank=True)

    def one_line_description(self):
        text = f"Prend en compte les précédences enregistrées en base."
        if self.train_progs.exists():
            text += ' des promos ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        if self.modules.exists():
            text += ' pour les modules ' + ', '.join([module.abbrev for module in self.modules.all()])
        return text

    def enrich_model(self, ttmodel, week, ponderation=10):
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

    def one_line_description(self):
        text = f"Prend en compte les pivots enregistrées en base."
        if self.train_progs.exists():
            text += ' des promos ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        if self.modules.exists():
            text += ' pour les modules ' + ', '.join([module.abbrev for module in self.modules.all()])
        return text

    def enrich_model(self, ttmodel, week, ponderation=10):
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


class AvoidBothTimes(TTConstraint):
    """
    Avoid the use of two slots
    Idéalement, on pourrait paramétrer slot1, et slot2 à partir de slot1... Genre slot1
    c'est 8h n'importe quel jour, et slot2 14h le même jour...
    """
    time1 = models.PositiveSmallIntegerField()
    time2 = models.PositiveSmallIntegerField()
    group = models.ForeignKey('base.Group', null=True, on_delete=models.CASCADE)
    tutor = models.ForeignKey('people.Tutor',
                              null=True,
                              default=None,
                              on_delete=models.CASCADE)

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(['group', 'tutor'])
        return attributes

    def enrich_model(self, ttmodel, week, ponderation=1):
        fc = self.get_courses_queryset_by_attributes(ttmodel, week)
        slots1 = set([slot for slot in ttmodel.wdb.courses_slots
                      if slot.start_time <= self.time1 < slot.end_time])
        slots2 = set([slot for slot in ttmodel.wdb.courses_slots
                      if slot.start_time <= self.time2 < slot.end_time])
        for c1 in fc:
            for c2 in fc.exclude(id__lte=c1.id):
                for sl1 in slots1:
                    for sl2 in slots2:
                        if self.weight is not None:
                            conj_var = ttmodel.add_conjunct(
                                ttmodel.TT[(sl1, c1)],
                                ttmodel.TT[(sl2, c2)])
                            ttmodel.add_to_generic_cost(self.local_weight() * ponderation * conj_var, week=week)
                        else:
                            ttmodel.add_constraint(ttmodel.TT[(sl1, c1)]
                                                   + ttmodel.TT[(sl2, c2)],
                                                   '<=',
                                                   1,
                                                   Constraint(constraint_type=ConstraintType.AVOID_BOTH_TIME,
                                                              instructors=self.tutor, groups=self.group))

    def one_line_description(self):
        text = f"Pas à la fois à {french_format(self.time1)} et à {french_format(self.time2)}"
        if self.tutor:
            text += ' pour ' + str(self.tutor)
        if self.group:
            text += ' avec le groupe ' + str(self.group)
        if self.train_progs.exists():
            text += ' des promos ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        else:
            text += " de toutes les promos."
        return text
