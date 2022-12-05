from datetime import datetime
from datetime import timedelta
from isoweek import Week

from django_ical.views import ICalFeed

from django.core.exceptions import ObjectDoesNotExist

from base.models import ScheduledCourse, Room, StructuralGroup, TransversalGroup, Day, Department, Regen
from people.models import Tutor
from django.db.models import Q

from django.http import HttpResponse, Http404
from django.utils.http import http_date
from calendar import timegm

def str_groups(c):
    groups = c.groups.all()
    gp_str = ', '.join([f'{g.train_prog.abbrev} {g.name}'
                        for g in groups])
    plural = len(groups) > 1
    return gp_str, plural


class EventFeed(ICalFeed):
    """
    A simple event calender
    """
    product_id = 'flop'
    timezone = 'Europe/Paris'
    days = [abbrev for abbrev,_ in Day.CHOICES]

    def item_title(self, scourse):
        course = scourse.course
        gp_str, plural = str_groups(course)
        return f'{course.module.abbrev} {course.type.name} - ' + gp_str

    def item_description(self, scourse):
        location = scourse.room.name if scourse.room is not None else ''
        course = scourse.course
        tutor = scourse.tutor
        ret = f'Cours : {course.module.abbrev} {course.type.name}\n'
        gp_str, plural = str_groups(course)
        ret += 'Groupe'
        if plural:
            ret += 's'
        ret += ' : '
        ret += gp_str
        ret += f'\nEnseignant·e : {tutor}\n'
        ret += f'Salle : {location}'
        return ret

    def item_start_datetime(self, scourse):
        course = scourse.course
        begin = datetime.combine(
            Week(course.week.year, course.week.nb)\
            .day(self.days.index(scourse.day)),
            datetime.min.time()) \
            + timedelta(minutes=scourse.start_time)
        return begin

    def item_end_datetime(self, scourse):
        end = self.item_start_datetime(scourse) \
            + timedelta(minutes=scourse.course.type.duration)
        return end

    def item_link(self, s):
        return str(s.id)


class TutorEventFeed(EventFeed):
    def get_object(self, request, department, tutor_id):
        return Tutor.objects.get(id=tutor_id)

    def items(self, tutor):
        return ScheduledCourse.objects.filter(Q(tutor=tutor) | Q(course__supp_tutor=tutor), work_copy=0)\
                                      .order_by('-course__week__year','-course__week__nb')

    def item_title(self, scourse):
        course = scourse.course
        location = scourse.room.name if scourse.room is not None else ''
        gp_str, plural = str_groups(course)
        return (f'{course.module.abbrev} {course.type.name} {"N°"+str(scourse.number) if scourse.number else ""} '
                f'- {gp_str} '
                f'- {location}'
        )


class RoomEventFeed(EventFeed):
    def get_object(self, request, department, room_id):
        return Room.objects.get(id=room_id).and_subrooms()

    def items(self, room_groups):
        return ScheduledCourse.objects\
                              .filter(room__in=room_groups, work_copy=0) \
            .order_by('-course__week__year', '-course__week__nb')

    def item_title(self, scourse):
        course = scourse.course
        gp_str, plural = str_groups(course)
        return (f'{course.module.abbrev} {course.type.name} '
                f'- {gp_str} '
                f'- {scourse.tutor.username if scourse.tutor is not None else "x"}'
        )


class GroupEventFeed(EventFeed):
    def get_object(self, request, department, group_id):
        raise NotImplementedError

    def items(self, groups):
        return ScheduledCourse.objects\
                              .filter(course__groups__in=groups, work_copy=0) \
            .order_by('-course__week__year', '-course__week__nb')

    def item_title(self, scourse):
        course = scourse.course
        location = scourse.room.name if scourse.room is not None else ''
        return (f'{course.module.abbrev} {course.type.name} '
                f'- {scourse.tutor.username if scourse.tutor is not None else "x"} '
                f'- {location}'
        )


class StructuralGroupEventFeed(GroupEventFeed):
    def get_object(self, request, department, group_id):
        gp = StructuralGroup.objects.get(id=group_id)
        return gp.structuralgroup.and_ancestors()


class TransversalGroupEventFeed(GroupEventFeed):
    def get_object(self, request, department, group_id):
        return {TransversalGroup.objects.get(id=group_id)}


class RegenFeed(ICalFeed):
    """
    A simple regen calender : one event per regeneration
    """
    product_id = 'flop'
    timezone = 'Europe/Paris'
    # TODO !

    def get_object(self, request, department, dep_id):
        dep = Department.objects.get(id=dep_id)
        return [dep]

    def items(self, departments):
        return Regen.objects.filter(department__in=departments)\
            .exclude(full=False, stabilize=False).order_by('-week__year','-week__nb')

    def item_title(self, regen):
        return f"flop!EDT - {regen.department.abbrev} : {regen.strplus()}"

    def item_description(self, regen):
        return self.item_title(regen)

    def item_start_datetime(self, regen):
        begin = Week(regen.week.year, regen.week.nb).day(0)
        return begin

    def item_end_datetime(self, regen):
        end = Week(regen.week.year, regen.week.nb).day(len(regen.department.timegeneralsettings.days))
        return end

    def item_link(self, s):
        return str(s.id)
