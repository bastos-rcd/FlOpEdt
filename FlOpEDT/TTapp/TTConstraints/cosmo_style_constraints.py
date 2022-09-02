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
from TTapp.ilp_constraints.constraint import Constraint
from TTapp.ilp_constraints.constraint_type import ConstraintType
from TTapp.slots import days_filter, slots_filter
from django.core.validators import MaxValueValidator
from django.utils.translation import gettext_lazy as _
from base.models import CourseStartTimeConstraint

slot_pause = 5

############################
# Tools for hole analysis
############################
def sum_of_courses_that_end_at(ttmodel, prof, day, end_time):
    res = ttmodel.sum(ttmodel.TTinstructors[sl, c, prof]
                      for sl in ttmodel.wdb.courses_slots if sl.end_time == end_time and sl.day == day
                      for c in ttmodel.wdb.compatible_courses[sl] & ttmodel.wdb.possible_courses[prof])
    return res


def sum_of_busy_slots_just_after(ttmodel, prof, day, end_time):
    res = ttmodel.sum(ttmodel.IBS[prof, sl_suivant]
                      for sl_suivant in slots_filter(ttmodel.wdb.availability_slots, starts_after=end_time,
                                                     starts_before=end_time + slot_pause, day=day))
    return res


class LimitHoles(TTConstraint):
    """
    Limit the total number of holes in each day, and every week
    """
    tutors = models.ManyToManyField('people.Tutor', blank=True)
    max_holes_per_day = models.PositiveSmallIntegerField(null=True, blank=True)
    max_holes_per_week = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = _('Limit holes')
        verbose_name_plural = verbose_name

    def get_viewmodel(self):
        view_model = super().get_viewmodel()
        details = view_model['details']

        if self.tutors.exists():
            details.update({'tutors': ', '.join([tutor.username for tutor in self.tutors.all()])})

        return view_model

    def one_line_description(self):
        text = "Limite le nombre de trous "
        if self.max_holes_per_day is not None:
            text += f"à {self.max_holes_per_day} par jour "
            if self.max_holes_per_week is not None:
                text += f"et "
        if self.max_holes_per_week is not None:
            text += f"à {self.max_holes_per_week} par semaine "
        if self.tutors.exists():
            text += ' pour : ' + ', '.join([tutor.username for tutor in self.tutors.all()])
        else:
            text += " pour tous les profs"
        if self.train_progs.exists():
            text += ' en ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        return text

    def enrich_ttmodel(self, ttmodel, week, ponderation=1):
        end_of_block = {}
        holes_nb = {}
        considered_tutors = set(ttmodel.wdb.instructors)
        if self.tutors.exists():
            considered_tutors &= set(self.tutors.all())

        for i in considered_tutors:
            for d in ttmodel.wdb.days:
                possible_end_times = list(set(sl.end_time for sl in slots_filter(ttmodel.wdb.courses_slots, day=d)))
                possible_end_times.sort()
                for end_time in possible_end_times:
                    end_of_block[i, end_time] = ttmodel.add_var()
                    # Si c'est une fin de bloc, un cours se termine là
                    ttmodel.add_constraint(
                        end_of_block[i, end_time] - sum_of_courses_that_end_at(ttmodel, i, d, end_time),
                        '<=', 0,
                        Constraint(constraint_type=ConstraintType.END_OF_BLOC,
                                   instructors=i, days=d,
                                   name="last->busy_%s_%s_%s" % (d, end_time, i.username))
                    )
                    # si c'est une fin de bloc, y'a pas de busy_slot juste après
                    ttmodel.add_constraint(
                        sum_of_busy_slots_just_after(ttmodel, i, d, end_time)
                        + 100 * end_of_block[i, end_time]
                        , '<=', 100,
                        Constraint(constraint_type=ConstraintType.END_OF_BLOC,
                                   instructors=i, days=d,
                                   name="last_%s_%s_%s_A" % (d, end_time, i.username))
                    )
                    # si c'est pas une fin de bloc, y'en a juste après OU y'en a pas qui se terminent là
                    ttmodel.add_constraint(
                        sum_of_busy_slots_just_after(ttmodel, i, d, end_time)
                        + (ttmodel.one_var - sum_of_courses_that_end_at(ttmodel, i, d, end_time))
                        + end_of_block[i, end_time]
                        , '>=', 1,
                        Constraint(constraint_type=ConstraintType.END_OF_BLOC,
                                   instructors=i, days=d,
                                   name="last_%s_%s_%s_B" % (d, end_time, i.username))
                    )

                holes_nb[i, d] = ttmodel.sum(end_of_block[i, end_time]
                                             for end_time in possible_end_times) - ttmodel.IBD[i, d]

                if self.max_holes_per_day:
                    if self.weight is None:
                        ttmodel.add_constraint(holes_nb[i, d], '<=', self.max_holes_per_day,
                                               Constraint(constraint_type=ConstraintType.MAX_HOLES,
                                                          instructors=i, days=d,
                                                          name="%g trous max %s %s" % (self.max_holes_per_day, i.username, d))
                                               )
                        #ttmodel.add_to_inst_cost(i, 10 * holes_nb[i, d], week)
                    else:
                        ttmodel.add_to_inst_cost(i, holes_nb[i, d] * self.local_weight(), week)
            if self.max_holes_per_week:
                total_holes = ttmodel.sum(holes_nb[i, d] for d in ttmodel.wdb.days)
                if self.weight is None:
                    ttmodel.add_constraint(total_holes, '<=', self.max_holes_per_week,
                                           Constraint(constraint_type=ConstraintType.MAX_HOLES))
                else:
                    unwanted = ttmodel.add_floor(total_holes, self.max_holes_per_week + 1, 10000)
                    ttmodel.add_to_inst_cost(i, unwanted * ponderation * self.local_weight(), week)


class LimitTutorTimePerWeeks(TTConstraint):
    tutors = models.ManyToManyField('people.Tutor', blank=True)
    min_time_per_period = models.PositiveSmallIntegerField(null=True, blank=True)
    max_time_per_period = models.PositiveSmallIntegerField(null=True, blank=True)
    tolerated_margin = models.PositiveSmallIntegerField(validators=[MaxValueValidator(100)], null=True, blank=True)
    number_of_weeks = models.PositiveSmallIntegerField(default=1, verbose_name=_("Number of weeks"))

    class Meta:
        verbose_name = _('Limit time per weeks for tutors')
        verbose_name_plural = verbose_name

    def get_viewmodel(self):
        view_model = super().get_viewmodel()
        details = view_model['details']

        if self.tutors.exists():
            details.update({'tutors': ', '.join([tutor.username for tutor in self.tutors.all()])})

        return view_model

    def one_line_description(self):
        text = "Temps de travail hebdomadaire "
        if self.min_time_per_period is not None:
            text += f"de {self.min_time_per_period} minimum "
            if self.max_time_per_period is not None:
                text += f"et "
        if self.max_time_per_period is not None:
            text += f"de {self.max_time_per_period} maximum "
        if self.tutors.exists():
            text += ' pour : ' + ', '.join([tutor.username for tutor in self.tutors.all()])
        else:
            text += " pour tous les profs"
        if self.train_progs.exists():
            text += ' en ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        if self.tolerated_margin:
            text += f" (avec une marge tolérée de {self.tolerated_margin}%)."
        return text

    def enrich_ttmodel(self, ttmodel, week, ponderation=1):
        # Do nothing if the number of weeks is less than excpected
        if len(ttmodel.weeks) < self.number_of_weeks:
            return
        if self.tutors.exists():
            tutors = set(t for t in ttmodel.wdb.instructors if t in self.tutors.all())
        else:
            tutors = set(ttmodel.wdb.instructors)
        local_weight = 1
        if self.weight is not None:
            local_weight = self.local_weight()
        # enrich model for each period of the desired length inside ttmodel.weeks
        for i in range(len(ttmodel.weeks) - self.number_of_weeks + 1):
            considered_weeks = ttmodel.weeks[i:i+self.number_of_weeks]
            for tutor in tutors:
                total_tutor_time = ttmodel.sum(ttmodel.TTinstructors[sl, c, tutor] * sl.duration
                                               for c in ttmodel.wdb.possible_courses[tutor]
                                               for sl in slots_filter(ttmodel.wdb.compatible_slots[c],
                                                                      week_in = considered_weeks)
                                               ) \
                                  + sum(sc.course.type.duration
                                        for sc in ttmodel.wdb.other_departments_scheduled_courses_for_tutor[tutor]
                                        if sc.course.week in considered_weeks)
                if self.max_time_per_period is not None:
                    undesirable_max = ttmodel.add_floor(total_tutor_time, self.max_time_per_period,
                                                        24 * 60 * 7 * self.number_of_weeks)
                    if self.tolerated_margin:
                        untolerable_max = ttmodel.add_floor(total_tutor_time,
                                                            self.max_time_per_period * (1 + self.tolerated_margin / 100),
                                                            24 * 60 * 7 * self.number_of_weeks)
                    else:
                        untolerable_max = undesirable_max

                    if self.weight is None:
                        ttmodel.add_constraint(untolerable_max,
                                               '==',
                                               0,
                                               Constraint(constraint_type=ConstraintType.max_time_per_week,
                                                          instructors=tutor))
                    else:
                        ttmodel.add_to_inst_cost(tutor, untolerable_max * local_weight * ponderation, week)
                    ttmodel.add_to_inst_cost(tutor, undesirable_max * local_weight * ponderation, week)
                if self.min_time_per_period is not None:
                    undesirable_min = ttmodel.one_var - ttmodel.add_floor(total_tutor_time, self.min_time_per_period,
                                                                          24 * 60 * 7 * self.number_of_weeks)
                    if self.tolerated_margin:
                        untolerable_min = ttmodel.one_var - ttmodel.add_floor(total_tutor_time,
                                                                              self.min_time_per_period * (1 - self.tolerated_margin / 100),
                                                                              24 * 60 * 7 * self.number_of_weeks)
                    else:
                        untolerable_min = undesirable_min

                    if self.weight is None:
                        ttmodel.add_constraint(untolerable_min,
                                               '==',
                                               0,
                                               Constraint(constraint_type=ConstraintType.min_time_per_week,
                                                          instructors=tutor))
                    else:
                        ttmodel.add_to_inst_cost(tutor, untolerable_min * local_weight * ponderation, week)
                    ttmodel.add_to_inst_cost(tutor, undesirable_min * local_weight * ponderation, week)


class ModulesByBloc(TTConstraint):
    """
    Force that same module is affected by bloc (a same tutor is affected to each bloc of same module)
    Except for suspens courses
    """
    modules = models.ManyToManyField('base.Module', blank=True)

    class Meta:
        verbose_name = _('Gather courses of considered modules')
        verbose_name_plural = verbose_name

    def get_viewmodel(self):
        view_model = super().get_viewmodel()
        details = view_model['details']

        if self.modules.exists():
            details.update({'modules': ', '.join([module.abbrev for module in self.modules.all()])})

        return view_model

    def one_line_description(self):
        text = "Modules "
        if self.modules.exists():
            text +=', '.join([module.abbrev for module in self.modules.all()])
        text += "are affected by bloc."
        return text

    def enrich_ttmodel(self, ttmodel, week, ponderation=1):
        if self.weight is not None:
            print("ModulesByBloc is available only for constraint, not preference...")
            return

        considered_modules = ttmodel.wdb.modules
        if self.modules.exists():
            considered_modules = set(considered_modules) & set(self.modules.all())
        if self.train_progs.exists():
            considered_modules = set(m for m in considered_modules if m.train_prog in self.train_progs.all())

        possible_start_times = set()
        for c in CourseStartTimeConstraint.objects.filter(course_type__department=ttmodel.department):
            possible_start_times |= set(c.allowed_start_times)
        possible_start_times = list(possible_start_times)
        possible_start_times.sort()

        for d in days_filter(ttmodel.wdb.days, week=week):
            day_slots = slots_filter(ttmodel.wdb.courses_slots, day=d)
            day_sched_courses = ttmodel.wdb.sched_courses.filter(day=d.day, course__week=week, course__suspens=False)
            for m in considered_modules:
                module_day_sched_courses = day_sched_courses.filter(course__module=m)
                if not module_day_sched_courses.exists():
                    continue
                for i in range(len(possible_start_times) - 1):
                    slot_sched_courses = module_day_sched_courses.filter(start_time=possible_start_times[i])
                    next_slot_sched_courses = module_day_sched_courses.filter(start_time=possible_start_times[i+1])
                    if not (slot_sched_courses.exists() and next_slot_sched_courses.exists()):
                        continue
                    slot = slots_filter(day_slots, start_time=possible_start_times[i]).pop()
                    next_slot = slots_filter(day_slots, start_time=possible_start_times[i+1]).pop()
                    # Choose the slot where more courses have to be assigned
                    if slot_sched_courses.count() == next_slot_sched_courses.count():
                        for tutor in ttmodel.wdb.possible_tutors[m]:
                            ttmodel.add_constraint(
                                ttmodel.sum(ttmodel.TTinstructors[(next_slot, sc2.course, tutor)]
                                            for sc2 in next_slot_sched_courses)
                                - ttmodel.sum(ttmodel.TTinstructors[(slot, sc.course, tutor)]
                                              for sc in slot_sched_courses),
                                '==',
                                0,
                                Constraint(constraint_type=ConstraintType.module_by_bloc,
                                           instructors=tutor, days=d, modules=m))
                    elif slot_sched_courses.count() > next_slot_sched_courses.count():
                        for tutor in ttmodel.wdb.possible_tutors[m]:
                            ttmodel.add_constraint(
                                2 * ttmodel.sum(ttmodel.TTinstructors[(next_slot, sc2.course, tutor)]
                                                for sc2 in next_slot_sched_courses)
                                - ttmodel.sum(ttmodel.TTinstructors[(slot, sc.course, tutor)]
                                              for sc in slot_sched_courses),
                                '<=',
                                1,
                                Constraint(constraint_type=ConstraintType.module_by_bloc,
                                           instructors=tutor, days=d, modules=m))
                    else: # slot_sched_courses.count() < next_slot_sched_courses.count()
                        for tutor in ttmodel.wdb.possible_tutors[m]:
                            ttmodel.add_constraint(
                                2 * ttmodel.sum(ttmodel.TTinstructors[(slot, sc.course, tutor)]
                                              for sc in slot_sched_courses)
                                - ttmodel.sum(ttmodel.TTinstructors[(next_slot, sc2.course, tutor)]
                                                for sc2 in next_slot_sched_courses),
                                '<=',
                                1,
                                Constraint(constraint_type=ConstraintType.module_by_bloc,
                                           instructors=tutor, days=d, modules=m))
