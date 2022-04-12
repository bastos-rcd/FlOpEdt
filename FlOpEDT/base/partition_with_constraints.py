from TTapp.TTConstraints.no_course_constraints import NoTutorCourseOnDay
import TTapp.TTConstraints.tools_centralized_preanalysis as tools
from base.partition import Partition
from base.models import CourseStartTimeConstraint, ModulePossibleTutors, ScheduledCourse, TimeGeneralSettings, UserPreference, StructuralGroup
from base.timing import TimeInterval, Day, days_index, flopdate_to_datetime, time_to_floptime
from datetime import datetime, timedelta
from django.db.models import Q
import copy

# TODO : move ?
def create_tutor_partition_from_constraints(week, department, tutor):
    """
        Create a partition and add information in some slots about all constraints implementing complete_tutor_partition.
        Those constraints are retrieved in the database and taken in account if they are applied on the week and
        the department given in parameters and that concern the given tutor.
        Constraints that can be taken in account : NoTutorCourseOnDay, NoGroupCourseOnDay, TutorLunchBreak, GroupLunchBreak.

    :param week: The Week we want to consider in a pre-analysis (can be None if constraint applied on all weeks).
    :param department: The Department on which constraints in a pre-analysis are applied.
    :param tutor: The Tutor used to create his partition.
    :return: A tutor's partition with more details about this tutor's availabilities or forbidden slots depending
    on defined constraints in the database.

    """
    print("Hello 2 !")

    # Init partition
    partition = Partition.get_partition_of_week(week, department, True)

    # Retrieve all existing constraints (inheriting directly or not from TTConstraints) in the database for the given
    # week and department
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


def complete_tutor_partition_from_constraints(partition, week, department, tutor):
    """

    :param partition:
    :param week:
    :param department:
    :param tutor:
    :return:
    """
    print("Hello 2 !")

    # Init partition
    # partition = Partition.get_partition_of_week(week, department, True)

    # Retrieve all existing constraints (inheriting directly or not from TTConstraints) in the database for the given
    # week and department
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
def create_group_partition_from_constraints(week, department, group):
    """
            Create a partition and add information in some slots about all constraints implementing complete_group_partition.
            Those constraints are retrieved in the database and taken in account if they are applied on the week and
            the department given in parameters and that concern the given group.
            Constraints that can be taken in account : NoTutorCourseOnDay, NoGroupCourseOnDay, TutorLunchBreak, GroupLunchBreak.

        :param week: The Week we want to consider in a pre-analysis (can be None if constraint applied on all weeks).
        :param department: The Department on which constraints in a pre-analysis are applied.
        :param group: The group used to create its partition.
        :return: A partition for a group with more details about this group's availabilities or forbidden slots depending
        on defined constraints in the database.

    """
    # Init partition
    partition = Partition.get_partition_of_week(week=week, department=department, with_day_time=True)

    # Retrieve all existing constraints (inheriting directly or not from TTConstraints) in the database for the given
    # week and department
    constraints_list = tools.getTTConstraintsInDB(week, department)

    # For each constraint (week and department considered) in the database, try to find the complete_group_partition
    # method and add information in the partition if found
    for constraint in constraints_list:
        try:
            partition = constraint.complete_group_partition(partition, group, week)
        except AttributeError:
            pass

    return partition

def complete_group_partition_from_constraints(partition, week, department, group):

    # Init partition
    # partition = Partition.get_partition_of_week(week, department, True)

    # Retrieve all existing constraints (inheriting directly or not from TTConstraints) in the database for the given
    # week and department
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

# TODO : modified (modifier si week = None)
def create_course_partition_from_constraints(course, week, department):
    
    week_partition = Partition.get_partition_of_week(week, department, True)
    
    possible_tutors_1 = set()
    required_supp_1 = set()
    
    if course.tutor is not None:
        possible_tutors_1.add(course.tutor)
        
    # TODO revoir cette partie
    elif ModulePossibleTutors.objects.filter(module=course.module).exists():
        possible_tutors_1 = set(ModulePossibleTutors.objects.get(module=course.module).possible_tutors.all())
    else:
        mods_possible_tutor = ModulePossibleTutors.objects.filter(module__train_prog__department=department)
        possible_tutors_1 = set(mod.possible_tutors.all() for mod in mods_possible_tutor)
    if course.supp_tutor is not None:
        required_supp_1 = set(course.supp_tutor.all())

    for tutor in possible_tutors_1:
        print(tutor.username)
        week_partition = complete_tutor_partition_from_constraints(week_partition, week, department, tutor)
    
    for tutor in required_supp_1:
        week_partition.tutor_supp = True
        week_partition = complete_tutor_partition_from_constraints(week_partition, week, department, tutor)

    groups = course.groups.all()
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
    
    return week_partition
