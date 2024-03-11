from django.db import models
from base.timing import Day, min_to_str
from base.models.courses import ScheduledCourse, ScheduledCourseAdditional
from base import weeks


class EdtVersion(models.Model):
    department = models.ForeignKey(
        "base.Department", on_delete=models.CASCADE, null=True
    )
    period = models.ForeignKey(
        "SchedulingPeriod", on_delete=models.CASCADE, null=True, blank=True
    )
    work_copy = models.PositiveSmallIntegerField(default=0)
    version = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = (("department", "period", "work_copy"),)


#    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


# null iff no change
class CourseModification(models.Model):
    course = models.ForeignKey("Course", on_delete=models.CASCADE)
    old_period = models.ForeignKey(
        "SchedulingPeriod", on_delete=models.CASCADE, null=True, blank=True
    )
    room_old = models.ForeignKey(
        "Room", blank=True, null=True, on_delete=models.CASCADE
    )
    day_old = models.CharField(
        max_length=2, choices=Day.CHOICES, default=None, null=True
    )
    start_time_old = models.DateTimeField(default=None, null=True)
    tutor_old = models.ForeignKey(
        "people.Tutor",
        related_name="impacted_by_course_modif",
        null=True,
        default=None,
        on_delete=models.SET_NULL,
    )
    version_old = models.PositiveIntegerField()
    updated_at = models.DateTimeField(auto_now=True)
    initiator = models.ForeignKey("people.User", on_delete=models.CASCADE)

    def strs_course_changes(self, course=None, sched_course=None):
        if course is None:
            course = self.course
        if sched_course is None:
            sched_course = ScheduledCourse.objects.get(course=course, work_copy=0)
        department = course.type.department
        al = "\n  · "
        same = f"- Cours {course.module.abbrev} semaine {course.period}"
        changed = ""

        tutor_old_name = (
            self.tutor_old.username if self.tutor_old is not None else "personne"
        )
        if sched_course.tutor == self.tutor_old:
            same += f", par {tutor_old_name}"
        else:
            cur_tutor_name = (
                sched_course.tutor.username
                if sched_course.tutor is not None
                else "personne"
            )
            changed += al + f"Prof : {tutor_old_name} -> {cur_tutor_name}"

        if sched_course.room is None:
            if ScheduledCourseAdditional.objects.filter(
                scheduled_course=sched_course
            ).exists():
                cur_room_name = "en visio"
            else:
                cur_room_name = "nulle part"
        else:
            cur_room_name = sched_course.room.name

        if sched_course.room == self.room_old:
            same += f", {cur_room_name}"
        else:
            room_old_name = (
                self.room_old.name if self.room_old is not None else "sans salle"
            )
            changed += al + f"Salle : {room_old_name} -> {cur_room_name}"

        day_list = weeks.num_all_days(course.week.year, course.week.nb, department)
        if (
            sched_course.day == self.day_old
            and sched_course.start_time == self.start_time_old
        ):
            for d in day_list:
                if d["ref"] == sched_course.day:
                    day = d
            same += (
                f', {day["name"]} {day["date"]} à {min_to_str(sched_course.start_time)}'
            )
        else:
            changed += al + "Horaire : "
            if self.day_old is None or self.start_time_old is None:
                changed += "non placé"
            else:
                for d in day_list:
                    if d["ref"] == self.day_old:
                        day = d
                changed += (
                    f'{day["name"]} {day["date"]} à {min_to_str(self.start_time_old)}'
                )
            changed += " -> "
            for d in day_list:
                if d["ref"] == sched_course.day:
                    day = d
            changed += (
                f'{day["name"]} {day["date"]} à {min_to_str(sched_course.start_time)}'
            )

        return same, changed

    def __str__(self):
        same, changed = self.strs_course_changes()
        if self.version_old is not None:
            same += f" ; (NumV {self.version_old})"
        ret = same + changed + f"\n  by {self.initiator.username}, at {self.updated_at}"
        return ret
