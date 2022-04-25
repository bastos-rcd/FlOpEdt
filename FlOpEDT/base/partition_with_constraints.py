from TTapp.TTConstraints.no_course_constraints import NoTutorCourseOnDay
import TTapp.TTConstraints.tools_centralized_preanalysis as tools
from base.partition import Partition
from base.models import CourseStartTimeConstraint, ModulePossibleTutors, ScheduledCourse, TimeGeneralSettings, UserPreference, StructuralGroup
from base.timing import TimeInterval, Day, days_index, flopdate_to_datetime, time_to_floptime
from datetime import datetime, timedelta
from django.db.models import Q
import copy

# TODO : modified (modifier si week = None)
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

# TODO : modified (modifier si week = None)
def complete_tutor_partition_from_constraints(partition, week, department, tutor):
    """

    :param partition:
    :param week:
    :param department:
    :param tutor:
    :return:
    
    """

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

# TODO : modified (modifier si week = None)
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

# TODO : modified (modifier si week = None)
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
    
    return week_partition
