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




from django.core.validators import MinValueValidator, MaxValueValidator

from django.db import models

# from django.contrib.auth.models import User

from django.core.exceptions import ValidationError

from django.utils.translation import ugettext_lazy as _

# from caching.base import CachingManager, CachingMixin

from base.models import Course, Time  # , Module

# class TestJour(models.Model):
#     jour = models.ForeignKey('modif.Jour', on_delete=models.CASCADE)
#     truc = models.CharField(max_length=10, verbose_name="Truc",default="")


max_weight = 8


class TTConstraint(models.Model):
    week = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(52)],
        null=True,
        default=None)
    year = models.PositiveSmallIntegerField(null=True, default=None)
    weight = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(max_weight)],
        null=True, default=None)
    comment = models.CharField(max_length=100, null=True, default=None, blank=True)
    is_active = models.BooleanField(verbose_name='Contrainte active?', default=True)

    def local_weight(self):
        return float(self.weight) / max_weight

    class Meta:
        abstract = True

    def enrich_model(self, ttmodel, ponderation=1):
        raise NotImplementedError


class LimitCourseTypePerPeriod(TTConstraint):  # , pond):
    """
    Bound the number of courses of type 'type' per day/half day
    Permet de limiter le nombre de cours du type 'type' par
    jour/demi-journee
    """
    type = models.ForeignKey('base.CourseType', on_delete=models.CASCADE)
    limit = models.PositiveSmallIntegerField()
    train_prog = models.ForeignKey('base.TrainingProgramme',
                                   null=True,
                                   default=None,
                                   on_delete=models.CASCADE)
    module = models.ForeignKey('base.Module', null=True, on_delete=models.CASCADE)
    tutor = models.ForeignKey('people.Tutor',
                              null=True,
                              default=None,
                              on_delete=models.CASCADE)
    FULL_DAY = 'fd'
    HALF_DAY = 'hd'
    PERIOD_CHOICES = ((FULL_DAY, 'Full day'), (HALF_DAY, 'Half day'))
    period = models.CharField(max_length=2, choices=PERIOD_CHOICES)

    def enrich_model(self, ttmodel, ponderation=1.):
        fc = ttmodel.wdb.courses
        if self.tutor is not None:
            fc = fc.filter(tutor=self.tutor)
        if self.module is not None:
            fc = fc.filter(module=self.module)
        if self.type is not None:
            fc = fc.filter(type=self.type)
        if self.train_prog is not None:
            fc = fc.filter(groupe__train_prog=self.train_prog)
        if self.period == self.FULL_DAY:
            periods = ['']
        else:
            periods = [Time.MATIN, Time.APREM]
        for d in ttmodel.wdb.days:
            for per in periods:
                expr = ttmodel.lin_expr()
                for sl in ttmodel.wdb.slots.filter(jour=d,
                                                   heure__apm__contains=per):
                    for c in fc:
                        expr += ttmodel.TT[(sl, c)]
                if self.weight is not None:
                    var = ttmodel.add_floor('limit course type per period', expr,
                                            int(self.limit) + 1, 100)
                    ttmodel.obj += self.local_weight() * ponderation * var
                else:
                    ttmodel.add_constraint(expr, '<=', self.limit)


class ReasonableDays(TTConstraint):
    """
    Allow to limit long days (with the first and last slot of a day). For a
    given parameter,
    a None value builds the constraint for all possible values,
    e.g. promo = None => the constraint holds for all promos.
    """
    train_prog = models.ForeignKey('base.TrainingProgramme',
                                   null=True,
                                   default=None,
                                   on_delete=models.CASCADE)
    group = models.ForeignKey('base.Group', null=True, on_delete=models.CASCADE)
    tutor = models.ForeignKey('people.Tutor',
                              null=True,
                              default=None,
                              on_delete=models.CASCADE)

    def enrich_model(self, ttmodel, ponderation=1):
        for d in ttmodel.wdb.days:
            slfirst = ttmodel.wdb.slots.get(heure__no=0, jour=d)
            sllast = ttmodel.wdb.slots.get(heure__no=5, jour=d)
            fc = ttmodel.wdb.courses
            if self.tutor is not None:
                fc = fc.filter(tutor=self.tutor)
            if self.train_prog is not None:
                fc = fc.filter(groupe__train_prog=self.train_prog)
            if self.group is not None:
                fc = fc.filter(groupe=self.group)
            for c1 in fc:
                for c2 in fc.exclude(id__lte=c1.id):
                    if self.weight is not None:
                        conj_var = ttmodel.add_conjunct(
                            ttmodel.TT[(slfirst, c1)],
                            ttmodel.TT[(sllast, c2)])
                        ttmodel.obj += self.local_weight() \
                                       * ponderation * conj_var
                    else:
                        ttmodel.add_constraint(ttmodel.TT[(slfirst, c1)] +
                                               ttmodel.TT[(sllast, c2)],
                                               '<=', 1)


class Stabilize(TTConstraint):
    """
    Allow to realy stabilize the courses of a category
    If general is true, none of the other (except week and work_copy) is
    relevant.
    --> In this case, each course c placed:
        - in a unused slot costs 1,
        - in a unused half day (for tutor and/or group) cost ponderation
    If general is False, it Fixes train_prog/tutor/group courses (or tries to if
    self.weight)
    """
    general = models.BooleanField(
        verbose_name='Stabiliser tout?',
        default=False)
    train_prog = models.ForeignKey('base.TrainingProgramme',
                                   null=True,
                                   default=None,
                                   on_delete=models.CASCADE)
    group = models.ForeignKey('base.Group', null=True, default=None, on_delete=models.CASCADE)
    module = models.ForeignKey('base.Module', null=True, default=None, on_delete=models.CASCADE)
    tutor = models.ForeignKey('people.Tutor',
                              null=True,
                              default=None,
                              on_delete=models.CASCADE)
    type = models.ForeignKey('base.CourseType', null=True, default=None, on_delete=models.CASCADE)
    work_copy = models.PositiveSmallIntegerField(default=0)

    def enrich_model(self, ttmodel, ponderation=1):
        if self.general:
            sched_courses = ttmodel.wdb.sched_courses \
                .filter(copie_travail=self.work_copy)
            # nb_changements_I=dict(zip(ttmodel.wdb.instructors,[0 for i in ttmodel.wdb.instructors]))
            for sl in ttmodel.wdb.slots:
                for c in ttmodel.wdb.courses:
                    if not sched_courses.filter(cours__tutor=c.tutor,
                                                creneau=sl,
                                                ):
                        ttmodel.obj += ttmodel.TT[(sl, c)]
                        # nb_changements_I[c.tutor]+=ttmodel.TT[(sl,c)]
                    if not sched_courses.filter(cours__tutor=c.tutor,
                                                creneau__jour=sl.jour,
                                                creneau__heure__apm=
                                                sl.heure.apm):
                        ttmodel.obj += ponderation * ttmodel.TT[(sl, c)]
                        # nb_changements_I[i]+=ttmodel.TT[(sl,c)]
                    if not sched_courses.filter(cours__groupe=c.groupe,
                                                creneau__jour=sl.jour,
                                                creneau__heure__apm=
                                                sl.heure.apm):
                        ttmodel.obj += ponderation * ttmodel.TT[(sl, c)]

        else:
            fc = ttmodel.wdb.courses
            if self.tutor is not None:
                fc = fc.filter(tutor=self.tutor)
            if self.type is not None:
                fc = fc.filter(type=self.type)
            if self.train_prog is not None:
                fc = fc.filter(groupe__train_prog=self.train_prog)
            if self.group:
                fc = fc.filter(groupe=self.group)
            if self.module:
                fc = fc.filter(module=self.module)
            for c in fc:
                sched_c = ttmodel.wdb \
                    .sched_courses \
                    .get(cours=c,
                         copie_travail=self.work_copy)
                chosen_slot = sched_c.creneau
                chosen_roomgroup = sched_c.room
                if self.weight is not None:
                    ttmodel.obj -= self.local_weight() \
                                   * ponderation * ttmodel.TT[(chosen_slot, c)]

                else:
                    ttmodel.add_constraint(ttmodel.TT[(chosen_slot, c)],
                                           '==',
                                           1)
                    if c.room_type in chosen_roomgroup.types.all():
                        ttmodel.add_constraint(
                            ttmodel.TTrooms[(chosen_slot, c, chosen_roomgroup)],
                            '==',
                            1)


class MinHalfDays(TTConstraint):
    """
    All courses will fit in a minimum of half days
    Optional : if 2 courses only, possibility to join it
    """
    module = models.ForeignKey('base.Module', null=True, on_delete=models.CASCADE)
    tutor = models.ForeignKey('people.Tutor',
                              null=True,
                              default=None,
                              on_delete=models.CASCADE)
    join2courses = models.BooleanField(
        verbose_name='If 2 or 4 courses only, join it?',
        default=False)

    def enrich_model(self, ttmodel, ponderation=1):
        fc = ttmodel.wdb.courses
        if self.tutor is not None:
            fc = fc.filter(tutor=self.tutor)
            b_h_ds = ttmodel.sum(
                ttmodel.IBHD[(self.tutor, d, apm)]
                for d in ttmodel.wdb.days
                for apm in [Time.MATIN, Time.APREM])
            local_var = ttmodel.add_var("MinIBHD_var_%s" % self.tutor)
        elif self.module is not None:
            local_var = ttmodel.add_var("MinMBHD_var_%s" % self.module)
            mod_b_h_d = {}
            for d in ttmodel.wdb.days:
                mod_b_h_d[(self.module, d, 'AM')] \
                    = ttmodel.add_var("ModBHD(%s,%s,%s)"
                                      % (self.module, d, 'AM'))
                mod_b_h_d[(self.module, d, 'PM')] \
                    = ttmodel.add_var("ModBHD(%s,%s,%s)"
                                      % (self.module, d, 'PM'))
                # add constraint linking MBHD to TT
                for apm in ['AM', 'PM']:
                    halfdayslots = ttmodel.wdb.slots.filter(jour=d,
                                                            heure__apm=apm)
                    card = len(halfdayslots)
                    expr = ttmodel.lin_expr()
                    expr += card * mod_b_h_d[(self.module, d, apm)]
                    for sl in halfdayslots:
                        for c in ttmodel.wdb.courses.filter(module=self.module):
                            expr -= ttmodel.TT[(sl, c)]
                    ttmodel.add_constraint(expr, '>=', 0)
                    ttmodel.add_constraint(expr, '<=', card - 1)
            fc = fc.filter(module=self.module)
            b_h_ds = ttmodel.sum(
                mod_b_h_d[(self.module, d, apm)]
                for d in ttmodel.wdb.days
                for apm in [Time.MATIN, Time.APREM])
        else:
            print("MinHalfDays must have module or prof --> Ignored")
            return

        ttmodel.add_constraint(local_var, '==', 1)
        limit = (len(fc) - 1) / 3 + 1

        if self.weight is not None:
            ttmodel.obj += self.local_weight() \
                           * ponderation \
                           * (b_h_ds - limit * local_var)
        else:
            ttmodel.add_constraint(b_h_ds, '<=', limit)

        if self.join2courses and len(fc) in [2, 4]:
            for d in ttmodel.wdb.days:
                sl8h = ttmodel.wdb.slots.get(jour=d, heure__no=0)
                sl11h = ttmodel.wdb.slots.get(jour=d, heure__no=2)
                sl14h = ttmodel.wdb.slots.get(jour=d, heure__no=3)
                sl17h = ttmodel.wdb.slots.get(jour=d, heure__no=5)
                for c in fc:
                    for c2 in fc.exclude(id=c.id):
                        ttmodel.add_constraint(
                            ttmodel.TT[(sl8h, c)] + ttmodel.TT[(sl11h, c2)],
                            '<=',
                            1)
                        ttmodel.add_constraint(
                            ttmodel.TT[(sl14h, c)] + ttmodel.TT[(sl17h, c2)],
                            '<=',
                            1)


class MinNonPreferedSlot(TTConstraint):
    """
    Minimize the use of unprefered Slots
    NB: You HAVE TO chose either tutor OR train_prog
    """
    tutor = models.ForeignKey('people.Tutor',
                              null=True,
                              default=None,
                              on_delete=models.CASCADE)
    train_prog = models.ForeignKey('base.TrainingProgramme',
                                   null=True,
                                   default=None,
                                   on_delete=models.CASCADE)

    # is not called when save() is
    def clean(self):
        if not self.tutor and not self.train_prog:
            raise ValidationError({
                'train_prog': ValidationError(_('Si pas de prof alors promo.',
                                                code='invalid')),
                'tutor': ValidationError(_('Si pas de promo alors prof.',
                                           code='invalid'))})

    def enrich_model(self, ttmodel, ponderation=1):
        if self.tutor is not None:
            filtered_courses = ttmodel.wdb.courses \
                .filter(tutor=self.tutor)
        else:
            filtered_courses = ttmodel.wdb.courses \
                .filter(groupe__train_prog=self.train_prog)
            # On exclut les cours de sport!
            filtered_courses = \
                filtered_courses.exclude(module__abbrev='SC')
        basic_groups = ttmodel.wdb.basic_groups \
            .filter(train_prog=self.train_prog)
        for sl in ttmodel.wdb.slots:
            for c in filtered_courses:
                if self.tutor is not None:
                    cost = (float(self.weight) / max_weight) \
                           * ponderation * ttmodel.TT[(sl, c)] \
                           * ttmodel.unp_slot_cost[c.tutor][sl]
                    ttmodel.add_to_slot_cost(sl, cost)
                    ttmodel.add_to_inst_cost(c.tutor, cost)
                else:
                    for g in basic_groups:
                        if c.groupe in ttmodel.wdb.basic_groups_surgroups[g]:
                            cost = self.local_weight() \
                                   * ponderation * ttmodel.TT[(sl, c)] \
                                   * ttmodel.unp_slot_cost_course[c.type,
                                                                  self.train_prog][sl]
                            ttmodel.add_to_group_cost(g, cost)
                            ttmodel.add_to_slot_cost(sl, cost)


class AvoidBothSlots(TTConstraint):
    """
    Avoid the use of two slots
    Idéalement, on pourrait paramétrer slot1, et slot2 à partir de slot1... Genre slot1
    c'est 8h n'importe quel jour, et slot2 14h le même jour...
    """
    slot1 = models.ForeignKey('base.Slot', related_name='slot1', on_delete=models.CASCADE)
    slot2 = models.ForeignKey('base.Slot', related_name='slot2', on_delete=models.CASCADE)
    train_prog = models.ForeignKey('base.TrainingProgramme',
                                   null=True,
                                   default=None,
                                   on_delete=models.CASCADE)
    group = models.ForeignKey('base.Group', null=True, on_delete=models.CASCADE)
    tutor = models.ForeignKey('people.Tutor',
                              null=True,
                              default=None,
                              on_delete=models.CASCADE)

    def enrich_model(self, ttmodel, ponderation=1):
        fc = ttmodel.wdb.courses
        if self.tutor is not None:
            fc = fc.filter(tutor=self.tutor)
        if self.train_prog is not None:
            fc = fc.filter(groupe__train_prog=self.train_prog)
        if self.group:
            fc = fc.filter(groupe=self.group)
        for c1 in fc:
            for c2 in fc.exclude(id__lte=c1.id):
                if self.weight is not None:
                    conj_var = ttmodel.add_conjunct(
                        ttmodel.TT[(self.slot1, c1)],
                        ttmodel.TT[(self.slot2, c2)])
                    ttmodel.obj += self.local_weight() * ponderation * conj_var
                else:
                    ttmodel.add_constraint(ttmodel.TT[(self.slot1, c1)]
                                           + ttmodel.TT[(self.slot2, c2)],
                                           '<=',
                                           1)


# class AvoidIsolatedSlot(TTConstraint):
#     """
#     Avoid the use of an isolated slot
#     RESTE A FAIRE (est-ce possible en non quadratique?)
#     """
#     train_prog = models.ForeignKey('base.TrainingProgramme',
#                                    null = True,
#                                    default = None,
#                                    on_delete=models.CASCADE)
#     group = models.ForeignKey('base.Groupe', null=True, on_delete=models.CASCADE)
#     tutor = models.ForeignKey('people.Tutor', null=True, on_delete=models.CASCADE)
#
#     def enrich_model(self, ttmodel, ponderation=1):
#         fc = ttmodel.wdb.courses
#         if self.tutor is not None:
#             fc = fc.filter(tutor = self.tutor)
#         if self.train_prog:
#             fc = fc.filter(groupe__train_prog = self.promo)
#         if self.group:
#             fc = fc.filter(groupe=self.group)


class SimultaneousCourses(TTConstraint):
    """
    Force two courses to be simultaneous
    It modifies the core constraints that impides such a simultaneity
    """
    course1 = models.ForeignKey('base.Course', related_name='course1', on_delete=models.CASCADE)
    course2 = models.ForeignKey('base.Course', related_name='course2', on_delete=models.CASCADE)

    def enrich_model(self, ttmodel, ponderation=1):
        same_tutor = (self.course1.tutor == self.course2.tutor)
        for sl in ttmodel.wdb.slots:
            var1 = ttmodel.TT[(sl, self.course1)]
            var2 = ttmodel.TT[(sl, self.course2)]
            ttmodel.add_constraint(var1 - var2, '==', 0)
            # A compléter, l'idée est que si les cours ont le même prof, ou des
            # groupes qui se superposent, il faut veiller à supprimer les core
            # constraints qui empêchent que les cours soient simultanés...
            if same_tutor:
                name_tutor_constr = str('core_tutor_'
                                        + str(self.course1.tutor)
                                        + '_'
                                        + str(sl))
                tutor_constr = ttmodel.get_constraint(name_tutor_constr)
                print(tutor_constr)
                if (ttmodel.var_coeff(var1, tutor_constr),
                    ttmodel.var_coeff(var2, tutor_constr)) == (1, 1):
                    ttmodel.change_var_coeff(var2, tutor_constr, 0)
            for bg in ttmodel.wdb.basic_groups:
                bg_groups = ttmodel.wdb.basic_groups_surgroups[bg]
                if self.course1.groupe in bg_groups \
                        and self.course2.groupe in bg_groups:
                    name_group_constr = 'core_group_' + str(bg) + '_' + str(sl)
                    group_constr = ttmodel.get_constraint(name_group_constr)
                    if (ttmodel.var_coeff(var1, group_constr),
                        ttmodel.var_coeff(var2, group_constr)) == (1, 1):
                        ttmodel.change_var_coeff(var2, group_constr, 0)
