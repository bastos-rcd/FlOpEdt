import datetime as dt

from django.db.models import Q
from django_ical.views import ICalFeed

from base.models import (
    Day,
    Department,
    Regen,
    Room,
    ScheduledCourse,
    StructuralGroup,
    TransversalGroup,
)
from people.models import Tutor
from roomreservation.models import RoomReservation


def str_groups(c):
    groups = c.groups.all()
    gp_str = ", ".join([f"{g.train_prog.abbrev} {g.name}" for g in groups])
    plural = len(groups) > 1
    return gp_str, plural


class EventFeed(ICalFeed):
    """
    A simple event calender
    """

    product_id = "flop"
    timezone = "Europe/Paris"
    days = [abbrev for abbrev, _ in Day.CHOICES]

    def item_title(self, item):
        scourse = item
        course = scourse.course
        gp_str, _ = str_groups(course)
        return f"{course.module.abbrev} {course.type.name} - " + gp_str

    def item_description(self, item):
        scourse = item
        location = scourse.room.name if scourse.room is not None else ""
        course = scourse.course
        tutor = scourse.tutor
        ret = f"Cours : {course.module.abbrev} {course.type.name}\n"
        gp_str, plural = str_groups(course)
        ret += "Groupe"
        if plural:
            ret += "s"
        ret += " : "
        ret += gp_str
        ret += f"\nEnseignant·e : {tutor}\n"
        ret += f"Salle : {location}"
        return ret

    def item_location(self, item: ScheduledCourse):
        scourse = item
        return scourse.room.name if scourse.room is not None else ""

    def item_start_datetime(self, item: ScheduledCourse):
        scourse = item
        return scourse.start_time

    def item_end_datetime(self, item: ScheduledCourse):
        scourse = item
        return scourse.end_time

    def item_link(self, item):
        return str(item.id)


class TutorEventFeed(EventFeed):
    def get_object(  # pylint: disable=arguments-differ
        self,
        request,
        department,  # pylint: disable=unused-argument
        tutor_id,
    ):
        return Tutor.objects.get(id=tutor_id)

    def items(self, tutor):
        return ScheduledCourse.objects.filter(
            Q(tutor=tutor) | Q(course__supp_tutors=tutor), version__major=0
        ).order_by("-start_time")

    def item_title(self, item):
        scourse = item
        course = scourse.course
        gp_str, _ = str_groups(course)
        return (
            f"{course.module.abbrev} {course.type.name} "
            f'{"N°"+str(scourse.number) if scourse.number else ""} '
            f"- {gp_str} "
        )


class RoomEventFeed(EventFeed):
    def get_object(  # pylint: disable=arguments-differ
        self, request, department, room_id  # pylint: disable=unused-argument
    ):
        return Room.objects.get(id=room_id).and_overrooms()

    def items(self, room_groups):
        room_scheduled_courses = ScheduledCourse.objects.filter(
            room__in=room_groups, version__major=0
        ).order_by("-start_time")
        room_reservations = RoomReservation.objects.filter(
            room__in=room_groups
        ).order_by("-date", "-start_time")
        return list(room_scheduled_courses) + list(room_reservations)

    def item_title(self, item):
        sched_course_or_reservation = item
        if isinstance(sched_course_or_reservation, ScheduledCourse):
            scourse = sched_course_or_reservation
            course = scourse.course
            gp_str, _ = str_groups(course)
            return (
                f"{course.module.abbrev} {course.type.name} "
                f"- {gp_str} "
                f'- {scourse.tutor.username if scourse.tutor is not None else "x"}'
            )
        if isinstance(sched_course_or_reservation, RoomReservation):
            reservation = sched_course_or_reservation
            return (
                f"{reservation.title} ({reservation.reservation_type.name} - "
                f"{reservation.responsible.username})"
            )
        raise TypeError("Has to be course or reservation")

    def item_description(self, item):
        sched_course_or_reservation = item
        if isinstance(sched_course_or_reservation, ScheduledCourse):
            return super().item_description(sched_course_or_reservation)
        if isinstance(sched_course_or_reservation, RoomReservation):
            reservation = sched_course_or_reservation
            ret = f"Réservation : {reservation.title} \n"
            ret += f"{reservation.reservation_type.name}\n"
            ret += f"Responsable : {reservation.responsible.username}\n"
            return ret
        raise TypeError("Has to be course or reservation")

    def item_start_datetime(self, item):
        sched_course_or_reservation = item
        if isinstance(sched_course_or_reservation, ScheduledCourse):
            return super().item_start_datetime(sched_course_or_reservation)
        if isinstance(sched_course_or_reservation, RoomReservation):
            reservation = sched_course_or_reservation
            return dt.datetime.combine(reservation.date, reservation.start_time)
        raise TypeError("Has to be course or reservation")

    def item_end_datetime(self, item):
        sched_course_or_reservation = item
        if isinstance(sched_course_or_reservation, ScheduledCourse):
            return super().item_end_datetime(sched_course_or_reservation)
        if isinstance(sched_course_or_reservation, RoomReservation):
            reservation = sched_course_or_reservation
            return dt.datetime.combine(reservation.date, reservation.end_time)
        raise TypeError("Has to be course or reservation")


class GroupEventFeed(EventFeed):
    def get_object(
        self, request, department, group_id
    ):  # pylint: disable=arguments-differ
        raise NotImplementedError

    def items(self, groups):
        return ScheduledCourse.objects.filter(
            course__groups__in=groups, version__major=0
        ).order_by("-start_time")

    def item_title(self, item):
        scourse = item
        course = scourse.course
        return (
            f"{course.module.abbrev} {course.type.name} "
            f'- {scourse.tutor.username if scourse.tutor is not None else "x"} '
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

    product_id = "flop"
    timezone = "Europe/Paris"

    def get_object(  # pylint: disable=arguments-differ
        self,
        request,
        department,  # pylint: disable=unused-argument
        dep_id,
    ):
        dep = Department.objects.get(id=dep_id)
        return [dep]

    def items(self, departments):
        return (
            Regen.objects.filter(department__in=departments)
            .exclude(full=False, stabilize=False)
            .order_by("-period")
        )

    def item_title(self, item):
        regen = item
        return f"flop!EDT - {regen.department.abbrev} : {regen.strplus()}"

    def item_description(self, item):
        regen = item
        return self.item_title(regen)

    def item_start_datetime(self, regen):
        return regen.period.start_date

    def item_end_datetime(self, regen):
        return regen.period.end_date

    def item_link(self, item):
        regen = item
        return str(regen.id)
