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
from django.db.models import Q

from core.decorators import timer

from TTapp.FlopConstraint import FlopConstraint
from TTapp.TTConstraints.TTConstraint import TTConstraint
from TTapp.slots import slots_filter

from TTapp.ilp_constraints.constraint_type import ConstraintType
from TTapp.ilp_constraints.constraint import Constraint
from django.utils.translation import gettext_lazy as _


class RoomConstraint(FlopConstraint):
    """
    Abstract parent class of specific constraints that users may define

    Attributes:
        department : the department concerned by the constraint. Has to be filled.
        weeks : the weeks for which the constraint should be applied. All if None.
        weight : from 1 to max_weight if the constraint is optional, depending on its importance
                 None if the constraint is necessary
        is_active : usefull to de-activate a Constraint just before the generation
    """
    class Meta:
        abstract = True

    @timer
    def enrich_room_model(self, room_model, week, ponderation=1):
        raise NotImplementedError

    def week_courses_queryset(self, room_model, week):
        return room_model.courses.filter(week=week)

    def get_courses_queryset_by_parameters(self, room_model, week,
                                           train_progs=None,
                                           train_prog=None,
                                           module=None,
                                           group=None,
                                           course_type=None,
                                           room_type=None,
                                           tutor=None):

        courses_qs = FlopConstraint.get_courses_queryset_by_parameters(self, room_model, week,
                                                                       train_progs=train_progs,
                                                                       train_prog=train_prog,
                                                                       module=module,
                                                                       group=group,
                                                                       course_type=course_type,
                                                                       room_type=room_type)
        if tutor is not None:
            return courses_qs.filter(Q(tutor=tutor) | Q(supp_tutor=tutor))
        else:
            return courses_qs

    def get_ttmodel_courses_queryset_by_parameters(self, ttmodel, week,
                                                   train_progs=None,
                                                   train_prog=None,
                                                   module=None,
                                                   group=None,
                                                   course_type=None,
                                                   room_type=None,
                                                   tutor=None):

        return TTConstraint.get_courses_queryset_by_parameters(self, ttmodel, week,
                                                               train_progs=train_progs,
                                                               train_prog=train_prog,
                                                               module=module,
                                                               group=group,
                                                               course_type=course_type,
                                                               room_type=room_type,
                                                               tutor=tutor)


class LimitSimultaneousRoomCourses(RoomConstraint):
    """
    Only one course for each considered room on simultaneous slots
    """
    rooms = models.ManyToManyField('base.Room', blank=True)
    can_combine_two_groups_if_no_tutor = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Limit simultaneous courses for rooms')
        verbose_name_plural = verbose_name

    def one_line_description(self):
        text =  f"Pas plus d'un cours à la fois dans "
        if self.rooms.exists():
            text += f"dans les salles {', '.join(room.name for room in self.rooms.all())}."
        else:
            text += "chaque salle"
        if self.can_combine_two_groups_if_no_tutor:
            text += " (2 groupes en autonomie peuvent y être mis ensemble)."
        else:
            text+='.'
        return text

    def enrich_ttmodel(self, ttmodel, week, ponderation=1):
        considered_rooms = set(ttmodel.wdb.basic_rooms)
        if self.rooms.exists():
            considered_rooms = considered_rooms & set(self.rooms.all())
        relevant_slots = slots_filter(ttmodel.wdb.availability_slots, week=week)

        for r in considered_rooms:
            for sl in relevant_slots:
                all_courses_sum = ttmodel.sum(ttmodel.TTrooms[(sl2, c, rg)]
                                              for (c, rg) in ttmodel.wdb.room_course_compat[r]
                                              for sl2 in slots_filter(ttmodel.wdb.compatible_slots[c], simultaneous_to=sl)
                                              )
                if self.can_combine_two_groups_if_no_tutor:
                    no_tutor_courses_sum = ttmodel.sum(ttmodel.TTrooms[(sl2, c, rg)]
                                                       for (c, rg) in ttmodel.wdb.room_course_compat[r]
                                                       if c.tutor is None
                                                       for sl2 in slots_filter(ttmodel.wdb.compatible_slots[c],
                                                                               simultaneous_to=sl)
                                                       )

                    tutor_courses_sum = ttmodel.sum(ttmodel.TTrooms[(sl2, c, rg)]
                                                    for (c, rg) in ttmodel.wdb.room_course_compat[r]
                                                    if c.tutor is not None
                                                    for sl2 in slots_filter(ttmodel.wdb.compatible_slots[c],
                                                                            simultaneous_to=sl)
                                                    )
                    if self.weight is None:
                        ttmodel.add_constraint(2 * tutor_courses_sum + no_tutor_courses_sum,
                                               '<=', 2 * ttmodel.avail_room[r][sl],
                                               Constraint(constraint_type=ConstraintType.CORE_ROOMS,
                                                          rooms=r, slots=sl))

                    else:
                        if not ttmodel.avail_room[r][sl]:
                            ttmodel.add_constraint(all_courses_sum,
                                                   '==', 0,
                                                   Constraint(constraint_type=ConstraintType.CORE_ROOMS,
                                                              rooms=r, slots=sl))
                        else:
                            undesired_situation = ttmodel.add_floor(2 * tutor_courses_sum + no_tutor_courses_sum,
                                                                    3,
                                                                    1000)
                            ttmodel.add_to_generic_cost(self.local_weight() * ponderation * undesired_situation, week=week)

                else:
                    if self.weight is None:
                        ttmodel.add_constraint(all_courses_sum,
                                               '<=', ttmodel.avail_room[r][sl],
                                               Constraint(constraint_type=ConstraintType.CORE_ROOMS,
                                                          rooms=r, slots=sl))
                    else:
                        if not ttmodel.avail_room[r][sl]:
                            ttmodel.add_constraint(all_courses_sum,
                                                   '==', 0,
                                                   Constraint(constraint_type=ConstraintType.CORE_ROOMS,
                                                              rooms=r, slots=sl))
                        else:
                            undesired_situation = ttmodel.add_floor(all_courses_sum,
                                                                    2,
                                                                    1000)
                            ttmodel.add_to_generic_cost(self.local_weight() * ponderation * undesired_situation, week=week)

    def enrich_room_model(self, room_model, week, ponderation=1.):
        considered_rooms = set(room_model.basic_rooms)
        if self.rooms.exists():
            considered_rooms = considered_rooms & set(self.rooms.all())
        for basic_room in considered_rooms:
            for sl in room_model.slots:
                all_courses_sum = room_model.sum(room_model.TTrooms[(course, room)]
                                                 for (course, room) in room_model.room_course_compat[basic_room]
                                                 if sl.is_simultaneous_to(room_model.corresponding_scheduled_course[course]))
                if self.can_combine_two_groups_if_no_tutor:
                    no_tutor_courses_sum = room_model.sum(room_model.TTrooms[(course, room)]
                                                          for (course, room) in room_model.room_course_compat[basic_room]
                                                          if course.tutor is None
                                                          and sl.is_simultaneous_to(room_model.corresponding_scheduled_course[course]))
                    tutor_courses_sum = room_model.sum(room_model.TTrooms[(course, room)]
                                                        for (course, room) in room_model.room_course_compat[basic_room]
                                                        if course.tutor is not None
                                                        and sl.is_simultaneous_to(room_model.corresponding_scheduled_course[course]))

                    if self.weight is None:
                        room_model.add_constraint(2 * tutor_courses_sum + no_tutor_courses_sum,
                                                  '<=', 2 * room_model.avail_room[basic_room][sl],
                                                  Constraint(constraint_type=ConstraintType.CORE_ROOMS,
                                                             rooms=basic_room, slots=sl))
                    else:
                        if not room_model.avail_room[basic_room][sl]:
                            room_model.add_constraint(all_courses_sum,
                                                      '==', 0,
                                                      Constraint(constraint_type=ConstraintType.CORE_ROOMS,
                                                                 rooms=basic_room, slots=sl))
                        else:
                            undesired_situation = room_model.add_floor(2 * tutor_courses_sum + no_tutor_courses_sum,
                                                                       3,
                                                                       1000)
                            room_model.add_to_generic_cost(self.local_weight() * ponderation * undesired_situation,
                                                           week=week)
                else:
                    if self.weight is None:
                        room_model.add_constraint(all_courses_sum,
                                                  '<=', room_model.avail_room[basic_room][sl],
                                                  Constraint(constraint_type=ConstraintType.CORE_ROOMS,
                                                             rooms=basic_room, slots=sl))
                    else:
                        if not room_model.avail_room[basic_room][sl]:
                            room_model.add_constraint(all_courses_sum,
                                                      '==', 0,
                                                      Constraint(constraint_type=ConstraintType.CORE_ROOMS,
                                                                 rooms=basic_room, slots=sl))
                        else:
                            undesired_situation = room_model.add_floor(all_courses_sum,
                                                                       room_model.avail_room[basic_room][sl] + 1,
                                                                       1000)
                            room_model.add_to_generic_cost(self.local_weight() * ponderation * undesired_situation,
                                                           week=week)


class LimitedRoomChoices(RoomConstraint):
    """
    Limit the possible rooms for the courses
    Attributes are cumulative :
        limit the room choice for the courses o f this/every tutor, of this/every module, for this/every group ...
    """
    train_progs = models.ManyToManyField('base.TrainingProgramme',
                                         blank=True)
    module = models.ForeignKey('base.Module',
                               null=True,
                               default=None,
                               blank=True,
                               on_delete=models.CASCADE)
    tutor = models.ForeignKey('people.Tutor',
                              null=True,
                              default=None,
                              blank=True,
                              on_delete=models.CASCADE)
    group = models.ForeignKey('base.StructuralGroup',
                              null=True,
                              default=None,
                              blank=True,
                              on_delete=models.CASCADE)
    course_type = models.ForeignKey('base.CourseType',
                              null=True,
                              default=None,
                              blank=True,
                              on_delete=models.CASCADE)
    possible_rooms = models.ManyToManyField('base.Room')

    class Meta:
        verbose_name = _('Limited room choices')
        verbose_name_plural = verbose_name

    def enrich_room_model(self, room_model, week, ponderation=1.):
        filtered_courses = self.get_courses_queryset_by_attributes(room_model, week)
        possible_rooms = self.possible_rooms.all()
        relevant_sum = room_model.sum(room_model.TTrooms[(course, room)]
                                      for course in filtered_courses
                                      for room in room_model.course_room_compat[course] if room not in possible_rooms)
        if self.weight is not None:
            room_model.add_to_generic_cost(self.local_weight() * ponderation * relevant_sum, week=week)
        else:
            room_model.add_constraint(relevant_sum, '==', 0,
                                      Constraint(constraint_type=ConstraintType.LIMITED_ROOM_CHOICES,
                                                 instructors=self.tutor, groups=self.group, modules=self.module,
                                                 rooms=possible_rooms))

    def enrich_ttmodel(self, ttmodel, week, ponderation=1.):
        fc = self.get_courses_queryset_by_attributes(ttmodel, week)
        possible_rooms = self.possible_rooms.all()
        if self.tutor is None:
            relevant_var_dic = ttmodel.TTrooms
        else:
            relevant_var_dic = {(sl, c, rg): ttmodel.add_conjunct(ttmodel.TTrooms[(sl, c, rg)],
                                                                  ttmodel.TTinstructors[sl, c, self.tutor])
                                for c in fc
                                for sl in ttmodel.wdb.compatible_slots[c]
                                for rg in ttmodel.wdb.course_rg_compat[c] if rg not in possible_rooms }
        relevant_sum = ttmodel.sum(relevant_var_dic[(sl, c, rg)]
                                   for c in fc
                                   for sl in ttmodel.wdb.compatible_slots[c]
                                   for rg in ttmodel.wdb.course_rg_compat[c] if rg not in possible_rooms)
        if self.weight is not None:
            ttmodel.add_to_generic_cost(self.local_weight() * ponderation * relevant_sum, week=week)
        else:
            ttmodel.add_constraint(relevant_sum, '==', 0,
                                   Constraint(constraint_type=ConstraintType.LIMITED_ROOM_CHOICES,
                                              instructors=self.tutor, groups=self.group, modules=self.module,
                                              rooms=possible_rooms))

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
        if self.group:
            text += ' avec le groupe ' + str(self.group)
        text += " ne peuvent avoir lieu qu'en salle "
        for sl in self.possible_rooms.values_list():
            text += str(sl) + ', '
        return text


class ConsiderRoomSorts(RoomConstraint):
    tutors = models.ManyToManyField('people.Tutor', blank=True)

    class Meta:
        verbose_name = _("Consider tutors rooms sorts")
        verbose_name_plural = verbose_name

    def enrich_room_model(self, room_model, week, ponderation=1.):
        for tutor in considered_tutors(self, room_model):
            tutor_courses = room_model.courses_for_tutor[tutor] & room_model.courses_for_week[week]
            room_sorts = room_model.tutor_room_sorts[tutor]
            for room_sort in room_sorts:
                room_type = room_sort.for_type
                if room_type not in room_model.courses_for_room_type:
                    continue
                considered_courses = tutor_courses & room_model.courses_for_room_type[room_type]
                preferred = room_sort.prefer
                unpreferred = room_sort.unprefer
                members = room_type.members.all()
                if preferred not in members or unpreferred not in members:
                    continue
                preferred_sum = room_model.sum(room_model.TTrooms[(course, preferred)]
                                               for course in considered_courses)
                unpreferred_sum = room_model.sum(room_model.TTrooms[(course, unpreferred)]
                                                 for course in considered_courses)
                room_model.add_to_inst_cost(tutor,
                                            self.local_weight() * ponderation * (unpreferred_sum - preferred_sum),
                                            week=week)


class LocateAllCourses(RoomConstraint):
    modules = models.ManyToManyField('base.Module', blank=True)
    groups = models.ManyToManyField('base.StructuralGroup', blank=True)
    course_types = models.ManyToManyField('base.CourseType', blank=True)

    class Meta:
        verbose_name = _('Assign a room to the courses')
        verbose_name_plural = verbose_name

    def considered_courses(self, courses_of_the_week):
        courses_to_consider = courses_of_the_week
        if self.modules.exists():
            courses_to_consider = set(c for c in courses_to_consider if c.module in self.modules.all())
        if self.course_types.exists():
            courses_to_consider = set(c for c in courses_to_consider if c.type in self.course_types.all())
        return courses_to_consider

    def enrich_ttmodel(self, ttmodel, week, ponderation=1):
        considered_courses = self.considered_courses(ttmodel.wdb.courses_by_week[week])
        for c in considered_courses:
            for sl in ttmodel.wdb.compatible_slots[c]:
                undesired_situation = ttmodel.TT[(sl, c)] - \
                                      ttmodel.sum(ttmodel.TTrooms[(sl, c, r)] for r in ttmodel.wdb.course_rg_compat[c])
                if self.weight is None:
                    ttmodel.add_constraint(undesired_situation,
                                           '==', 0,
                                           Constraint(constraint_type=ConstraintType.LOCATE_ALL_COURSES,
                                                      slots=sl, courses=c))
                else:
                    ttmodel.add_to_slot_cost(sl, undesired_situation * self.local_weight() * ponderation, week)

    def enrich_room_model(self, room_model, week, ponderation=1):
        considered_courses = self.considered_courses(room_model.courses_for_week[week])
        for course in considered_courses:
            relevant_sum = room_model.sum(room_model.TTrooms[(course, room)]
                                          for room in room_model.course_room_compat[course])
            if self.weight is None:
                room_model.add_constraint(relevant_sum, '==', 1,
                                          Constraint(constraint_type=ConstraintType.LOCATE_ALL_COURSES,
                                                     courses=course))
            else:
                room_model.add_to_generic_cost((room_model.one_var - relevant_sum) * self.local_weight() * ponderation,
                                               week)

class LimitMoves(RoomConstraint):
    class Meta:
        abstract = True

    @property
    def ponderation(self):
        raise NotImplementedError

    def objects_to_consider(self, room_model):
        raise NotImplementedError

    def courses_dict(self, room_model):
        raise NotImplementedError

    def add_to_obj_method(self, room_model):
        raise NotImplementedError

    def enrich_room_model(self, room_model, week, ponderation=1):
        for thing in self.objects_to_consider(room_model):
            considered_courses = self.courses_dict(room_model)[thing] & room_model.courses_for_week[week]
            for course in considered_courses:
                scheduled_course = room_model.corresponding_scheduled_course[course]
                successors = set(c for c in considered_courses if
                                 room_model.corresponding_scheduled_course[c].is_successor_of(scheduled_course))
                if successors:
                    successor = successors.pop()
                    common_rooms = room_model.course_room_compat[course] & room_model.course_room_compat[successor]
                    same = room_model.sum(room_model.add_conjunct(room_model.TTrooms[(course, room)],
                                                                  room_model.TTrooms[(successor, room)])
                                          for room in common_rooms)
                    cost = - self.ponderation * self.local_weight() * ponderation * same
                    self.add_to_obj_method(room_model)(thing, cost, week)


class LimitGroupMoves(LimitMoves):
    groups = models.ManyToManyField('base.StructuralGroup', blank=True)

    class Meta:
        verbose_name = _('Limit room moves for groups')
        verbose_name_plural = verbose_name

    def objects_to_consider(self, room_model):
        return considered_basic_groups(self, room_model)

    def courses_dict(self, room_model):
        return room_model.courses_for_basic_group

    def add_to_obj_method(self, room_model):
        return room_model.add_to_group_cost

    @property
    def ponderation(self):
        return 2

class LimitTutorMoves(LimitMoves):
    tutors = models.ManyToManyField('people.Tutor', blank=True)

    class Meta:
        verbose_name = _('Limit room moves for tutors')
        verbose_name_plural = verbose_name

    def objects_to_consider(self, room_model):
        return considered_tutors(self, room_model)

    def courses_dict(self, room_model):
        return room_model.courses_for_tutor

    def add_to_obj_method(self, room_model):
        return room_model.add_to_inst_cost

    @property
    def ponderation(self):
        return 1

def considered_tutors(tutors_room_constraint, room_model):
    tutors_to_consider = set(room_model.tutors)
    if tutors_room_constraint.tutors.exists():
        tutors_to_consider &= set(tutors_room_constraint.tutors.all())
    return tutors_to_consider


def considered_basic_groups(group_room_constraint, room_model):
    room_model_basic_groups = set(room_model.basic_groups)
    if group_room_constraint.groups.exists():
        basic_groups = set()
        for g in group_room_constraint.groups.all():
            basic_groups |= g.basic_groups()
        room_model_basic_groups &= basic_groups
    return room_model_basic_groups