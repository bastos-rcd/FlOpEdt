from TTapp.GlobalPreAnalysis.tools_centralized_preanalysis import getFlopConstraintsInDB
from base.partition import Partition
from base.models import ModulePossibleTutors

def create_tutor_partition_from_constraints(week, department, tutor, available = False):
    """
        Create a partition and add information in some slots about all constraints implementing complete_tutor_partition.
    Those constraints are retrieved in the database and taken in account if they are applied on the week and
    the department given in parameters and that concern the given tutor.
    Constraints that can be taken in account : NoTutorCourseOnDay, NoGroupCourseOnDay, TutorLunchBreak, GroupLunchBreak.

    :param week: The Week we want to consider in a pre-analysis.
    :param department: The Department on which constraints in a pre-analysis are applied.
    :param tutor: The Tutor used to create his partition.
    :return: A tutor's partition with more details about this tutor's availabilities or forbidden slots depending
    on defined constraints in the database.

    """
    
    # Init partition
    partition = Partition.get_partition_of_week(week, department, True, available=available)

    # Retrieve all existing constraints (inheriting directly or not from TTConstraints) in the database for the given
    # week and department
    constraints_list = getFlopConstraintsInDB(week, department)

    for constraint in constraints_list:
        try:
            partition = constraint.complete_tutor_partition(partition, tutor, week)
        except AttributeError:
            pass

    return partition


def complete_tutor_partition_from_constraints(partition, week, department, tutor):
    """
        Complete a partition and add information in some slots about all constraints implementing complete_tutor_partition.
    Those constraints are retrieved in the database and taken in account if they are applied on the week and
    the department given in parameters and that concern the given tutor.
    Constraints that can be taken in account : NoTutorCourseOnDay, NoGroupCourseOnDay, TutorLunchBreak, GroupLunchBreak.

    :param partition: The partition we want to add information to.
    :param week: The Week we want to consider in a pre-analysis.
    :param department: The Department on which constraints in a pre-analysis are applied.
    :param tutor: The Tutor used to create his partition.
    :return: A tutor's partition with more details about this tutor's availabilities or forbidden slots depending
    on defined constraints in the database.
    
    """

    # Retrieve all existing constraints (inheriting directly or not from TTConstraints) in the database for the given
    # week and department
    constraints_list = tools.getFlopConstraintsInDB(week, department)

    for constraint in constraints_list:
        try:
            partition = constraint.complete_tutor_partition(partition, tutor, week)
        except AttributeError:
            pass

    return partition


def create_group_partition_from_constraints(week, department, group, available = False):
    """
        Create a partition and add information in some slots about all constraints implementing complete_group_partition.
    Those constraints are retrieved in the database and taken in account if they are applied on the week and
    the department given in parameters and that concern the given group.
    Constraints that can be taken in account : NoTutorCourseOnDay, NoGroupCourseOnDay, TutorLunchBreak, GroupLunchBreak.

    :param week: The Week we want to consider in a pre-analysis.
    :param department: The Department on which constraints in a pre-analysis are applied.
    :param group: The group used to create its partition.
    :return: A partition for a group with more details about this group's availabilities or forbidden slots depending
    on defined constraints in the database.

    """
    # Init partition
    partition = Partition.get_partition_of_week(week=week, department=department, with_day_time=True, available = available)

    # Retrieve all existing constraints (inheriting directly or not from TTConstraints) in the database for the given
    # week and department
    constraints_list = tools.getFlopConstraintsInDB(week, department)
    # For each constraint (week and department considered) in the database, try to find the complete_group_partition
    # method and add information in the partition if found
    for constraint in constraints_list:
        try:
            partition = constraint.complete_group_partition(partition, group, week)
        except AttributeError:
            pass

    return partition


def complete_group_partition_from_constraints(partition, week, department, group):
    """
        Complete a partition and add information in some slots about all constraints implementing complete_group_partition.
    Those constraints are retrieved in the database and taken in account if they are applied on the week and
    the department given in parameters and that concern the given group.
    Constraints that can be taken in account : NoTutorCourseOnDay, NoGroupCourseOnDay, TutorLunchBreak, GroupLunchBreak.

    :param partition: The partition we want to add information to.
    :param week: The Week we want to consider in a pre-analysis.
    :param department: The Department on which constraints in a pre-analysis are applied.
    :param group: The group used to create its partition.
    :return: A partition for a group with more details about this group's availabilities or forbidden slots depending
    on defined constraints in the database.

    """

    # Retrieve all existing constraints (inheriting directly or not from TTConstraints) in the database for the given
    # week and department
    constraints_list = tools.getFlopConstraintsInDB(week, department)

    for constraint in constraints_list:
        try:
            partition = constraint.complete_group_partition(partition, group, week)
        except AttributeError:
            pass

    return partition


def create_course_partition_from_constraints(course, week, department, available = False):
    """
        Create a partition with information about the tutors' and supp tutors' availabilities and the group's
    availabilities concerned by the course given in parameters. Those availabilities are given by existing constraints
    in the database for the given week and department.

    :param course: A course we want data about.
    :param week: The Week we want to consider in a pre-analysis.
    :param department: The Department on which constraints in a pre-analysis are applied.
    :return: A partition with more information about the course's possible slots.

    """

    # Init
    week_partition = Partition.get_partition_of_week(week, department, True, available = available)
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
        week_partition = complete_tutor_partition_from_constraints(week_partition, week, department, tutor)
    
    for tutor in required_supp_1:
        week_partition.tutor_supp = True
        week_partition = complete_tutor_partition_from_constraints(week_partition, week, department, tutor)

    # Groups
    groups = course.groups.all()
    for group in groups:
        week_partition = complete_group_partition_from_constraints(week_partition, week, department, group)
    
    return week_partition
