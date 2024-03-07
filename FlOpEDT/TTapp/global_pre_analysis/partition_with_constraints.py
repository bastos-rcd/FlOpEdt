from TTapp.global_pre_analysis.tools_centralized_preanalysis import getFlopConstraintsInDB
from base.partition import Partition
from base.models import ModulePossibleTutors

def create_tutor_partition_from_constraints(period, department, tutor, available = False):
    """
        Create a partition and add information in some slots about all constraints implementing complete_tutor_partition.
    Those constraints are retrieved in the database and taken in account if they are applied on the period and
    the department given in parameters and that concern the given tutor.
    Constraints that can be taken in account : NoTutorCourseOnDay, NoGroupCourseOnDay, TutorLunchBreak, GroupLunchBreak.

    :param period: The SchedulingPeriod we want to consider in a pre-analysis.
    :param department: The Department on which constraints in a pre-analysis are applied.
    :param tutor: The Tutor used to create his partition.
    :return: A tutor's partition with more details about this tutor's availabilities or forbidden slots depending
    on defined constraints in the database.

    """
    
    # Init partition
    partition = Partition.get_partition_of_period(period, department, True, available=available)

    # Retrieve all existing constraints (inheriting directly or not from TTConstraints) in the database for the given
    # period and department
    constraints_list = getFlopConstraintsInDB(period, department)

    for constraint in constraints_list:
        try:
            partition = constraint.complete_tutor_partition(partition, tutor, period)
        except AttributeError:
            pass

    return partition


def complete_tutor_partition_from_constraints(partition, period, department, tutor):
    """
        Complete a partition and add information in some slots about all constraints implementing complete_tutor_partition.
    Those constraints are retrieved in the database and taken in account if they are applied on the period and
    the department given in parameters and that concern the given tutor.
    Constraints that can be taken in account : NoTutorCourseOnDay, NoGroupCourseOnDay, TutorLunchBreak, GroupLunchBreak.

    :param partition: The partition we want to add information to.
    :param period: The SchedulingPeriod we want to consider in a pre-analysis.
    :param department: The Department on which constraints in a pre-analysis are applied.
    :param tutor: The Tutor used to create his partition.
    :return: A tutor's partition with more details about this tutor's availabilities or forbidden slots depending
    on defined constraints in the database.
    
    """

    # Retrieve all existing constraints (inheriting directly or not from TTConstraints) in the database for the given
    # period and department
    constraints_list = getFlopConstraintsInDB(period, department)

    for constraint in constraints_list:
        try:
            partition = constraint.complete_tutor_partition(partition, tutor, period)
        except AttributeError:
            pass

    return partition


def create_group_partition_from_constraints(period, department, group, available = False):
    """
        Create a partition and add information in some slots about all constraints implementing complete_group_partition.
    Those constraints are retrieved in the database and taken in account if they are applied on the period and
    the department given in parameters and that concern the given group.
    Constraints that can be taken in account : NoTutorCourseOnDay, NoGroupCourseOnDay, TutorLunchBreak, GroupLunchBreak.

    :param period: The SchedulingPeriod we want to consider in a pre-analysis.
    :param department: The Department on which constraints in a pre-analysis are applied.
    :param group: The group used to create its partition.
    :return: A partition for a group with more details about this group's availabilities or forbidden slots depending
    on defined constraints in the database.

    """
    # Init partition
    partition = Partition.get_partition_of_period(period=period, department=department, with_day_time=True, available = available)

    # Retrieve all existing constraints (inheriting directly or not from TTConstraints) in the database for the given
    # period and department
    constraints_list = getFlopConstraintsInDB(period, department)
    # For each constraint (period and department considered) in the database, try to find the complete_group_partition
    # method and add information in the partition if found
    for constraint in constraints_list:
        try:
            partition = constraint.complete_group_partition(partition, group, period)
        except AttributeError:
            pass

    return partition


def complete_group_partition_from_constraints(partition, period, department, group):
    """
        Complete a partition and add information in some slots about all constraints implementing complete_group_partition.
    Those constraints are retrieved in the database and taken in account if they are applied on the period and
    the department given in parameters and that concern the given group.
    Constraints that can be taken in account : NoTutorCourseOnDay, NoGroupCourseOnDay, TutorLunchBreak, GroupLunchBreak.

    :param partition: The partition we want to add information to.
    :param period: The SchedulingPeriod we want to consider in a pre-analysis.
    :param department: The Department on which constraints in a pre-analysis are applied.
    :param group: The group used to create its partition.
    :return: A partition for a group with more details about this group's availabilities or forbidden slots depending
    on defined constraints in the database.

    """

    # Retrieve all existing constraints (inheriting directly or not from TTConstraints) in the database for the given
    # period and department
    constraints_list = getFlopConstraintsInDB(period, department)

    for constraint in constraints_list:
        try:
            partition = constraint.complete_group_partition(partition, group, period)
        except AttributeError:
            pass

    return partition


def create_course_partition_from_constraints(course, period, department, available = False):
    """
        Create a partition with information about the tutors' and supp tutors' availabilities and the group's
    availabilities concerned by the course given in parameters. Those availabilities are given by existing constraints
    in the database for the given period and department.

    :param course: A course we want data about.
    :param period: The SchedulingPeriod we want to consider in a pre-analysis.
    :param department: The Department on which constraints in a pre-analysis are applied.
    :return: A partition with more information about the course's possible slots.

    """

    # Init
    period_partition = Partition.get_partition_of_period(period, department, True, available = available)
    possible_tutors_1 = set()
    required_supp_1 = set()

    # Tutors
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
        period_partition = complete_tutor_partition_from_constraints(period_partition, period, department, tutor)
    
    for tutor in required_supp_1:
        period_partition.tutor_supp = True
        period_partition = complete_tutor_partition_from_constraints(period_partition, period, department, tutor)

    # Groups
    groups = course.groups.all()
    for group in groups:
        period_partition = complete_group_partition_from_constraints(period_partition, period, department, group)
    
    return period_partition
