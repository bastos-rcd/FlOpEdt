from TTapp.TTConstraints.no_course_constraints import NoTutorCourseOnDay
import TTapp.TTConstraints.tools_centralized_preanalysis as tools
from base.partition import Partition
from base.models import CourseStartTimeConstraint, ModulePossibleTutors, ScheduledCourse, TimeGeneralSettings, UserPreference, StructuralGroup
from base.timing import TimeInterval, Day, days_index, flopdate_to_datetime, time_to_floptime
from datetime import datetime, timedelta
from django.db.models import Q
import copy

# TODO : move ?
def create_tutor_partition_from_constraints(week, department, tutor=None):
    print("Hello 2 !")

    # Init partition
    partition = Partition.get_partition_of_week(week, department, True)

    constraints_list = tools.getTTConstraintsInDB(week, department)

    for constraint in constraints_list:
        try:
            print("------------------------------------------")
            print(constraint)
            print(constraint.weeks.all())
            print("------------------------------------------")

            partition = constraint.complete_tutor_partition(partition, tutor, week)
        except AttributeError:
            pass

    return partition


def complete_tutor_partition_from_constraints(partition, week, department, tutor=None):
    print("Hello 2 !")

    # Init partition
    # partition = Partition.get_partition_of_week(week, department, True)

    constraints_list = tools.getTTConstraintsInDB(week, department)

    for constraint in constraints_list:
        try:
            print("------------------------------------------")
            print(constraint)
            print(constraint.weeks.all())
            print("------------------------------------------")

            partition = constraint.complete_tutor_partition(partition, tutor, week)
        except AttributeError:
            pass

    return partition


# TODO : a bouger dans partition ?
def create_group_partition_from_constraints(self, week, department, group=None):
    # Init partition
    partition = Partition.get_partition_of_week(week, department, True)

    constraints_list = tools.getTTConstraintsInDB(week, department)

    for constraint in constraints_list:
        try:
            partition = constraint.complete_group_partition(partition, group, week)
        except AttributeError:
            pass

    return partition

def complete_group_partition_from_constraints(partition, week, department, group=None):
    print("Hello 2 !")

    # Init partition
    # partition = Partition.get_partition_of_week(week, department, True)

    constraints_list = tools.getTTConstraintsInDB(week, department)

    for constraint in constraints_list:
        try:
            print("------------------------------------------")
            print(constraint)
            print(constraint.weeks.all())
            print("------------------------------------------")

            partition = constraint.complete_group_partition(partition, group, week)
        except AttributeError:
            pass

    return partition

# TODO : modified
def create_course_partition_from_constraints(course, week, department):
    week_partition = Partition.get_partition_of_week(week, department, True)
    possible_tutors_1 = set()
    required_supp_1 = set()
    print("[OK1] : ",course.tutor)
    if course.tutor is not None:
        possible_tutors_1.add(course.tutor)
    elif ModulePossibleTutors.objects.filter(module=course.module).exists():
        possible_tutors_1 = set(ModulePossibleTutors.objects.get(module=course.module).possible_tutors.all())
    else:
        mods_possible_tutor = ModulePossibleTutors.objects.filter(module__train_prog__department=department)
        possible_tutors_1 = set(mod.possible_tutors.all() for mod in mods_possible_tutor)

    if course.supp_tutor is not None:
        required_supp_1 = set(course.supp_tutor.all())

    print("[OK2] : ", required_supp_1)
    for tutor in possible_tutors_1:
        print(tutor.username)
        week_partition = complete_tutor_partition_from_constraints(week_partition, week, department, tutor)

    groups = course.groups.all()
    print("GROUPS:",groups)
    for group in groups:
        print(group.name)
        week_partition = complete_group_partition_from_constraints(week_partition, week, department, group)


    '''D1 = UserPreference.objects.filter(user__in=possible_tutors_1, week=week, value__gte=1)
    if not D1:
        D1 = UserPreference.objects.filter(user__in=possible_tutors_1, week=None, value__gte=1)
    if D1:
        # Retrieving constraints for days were tutors shouldn't be working
        # TODO : week_partition = completeTutorPartitionFromTTConstraints
        no_course_tutor1 = (NoTutorCourseOnDay.objects
            .filter(Q(tutors__in = required_supp_1.union(possible_tutors_1))
                | Q(tutor_status = [pt.status for pt in required_supp_1.union(possible_tutors_1)]),
                weeks = week))
        if not no_course_tutor1:
            no_course_tutor1 = (NoTutorCourseOnDay.objects
            .filter(Q(tutors__in = required_supp_1.union(possible_tutors_1))
                | Q(tutor_status = [pt.status for pt in required_supp_1.union(possible_tutors_1)]),
                weeks = None))

        # Adding all user preferences to the partition
        for up in D1:
            up_day = Day(up.day, week)
            week_partition.add_slot(
                TimeInterval(flopdate_to_datetime(up_day, up.start_time),
                flopdate_to_datetime(up_day, up.end_time)),
                "user_preference",
                {"value" : up.value, "available" : True, "tutor" : up.user}
            )

        # Retrieving no tutor course constraint slots and adding them to the partition
        # Slots are not set to be forbidden
        for constraint in no_course_tutor1:
            slot = constraint.get_slot_constraint(week)
            if slot:
                week_partition.add_slot(
                    slot[0],
                    "no_course_tutor",
                    slot[1]
                )

        for interval in week_partition.intervals:
            if not NoTutorCourseOnDay.tutor_and_supp(interval, required_supp_1, possible_tutors_1):
                interval[1]["available"] = False

        if required_supp_1:
            # Retrieving and adding user preferences for the required tutors
            RUS1 = UserPreference.objects.filter(user__in=required_supp_1, week=week, value__gte=1)
            if not RUS1:
                RUS1 = UserPreference.objects.filter(user__in=required_supp_1, week=None, value__gte=1)

            for up in RUS1:
                up_day = Day(up.day, week)
                week_partition.add_slot(
                    TimeInterval(flopdate_to_datetime(up_day, up.start_time),
                                 flopdate_to_datetime(up_day, up.end_time)),
                    "user_preference",
                    {"value": up.value, "available": True, "tutor": up.user}
                )

            for interval in week_partition.intervals:
                if not NoTutorCourseOnDay.tutor_and_supp(interval, required_supp_1, possible_tutors_1):
                    interval[1]["available"] = False
        return week_partition
    return None'''
    print(week_partition.intervals)
    return week_partition