from TTapp.TTConstraints.TTConstraint import TTConstraint
from django.db.models import Q

# This file contains functions that are used to get data on subclasses and especially about TTConstraints

def all_constraint_subclasses(class_name):
    """
        A class that returns all the subclasses (recursively) that inherits from the given class.

    :param class_name: The class we want to get all subclasses from
    :return: A set of subclasses

    """
    constraint_subclasses = set(class_name.__subclasses__())

    for subclass in class_name.__subclasses__():
        constraint_subclasses = constraint_subclasses.union(all_constraint_subclasses(subclass))

    return constraint_subclasses


def all_TTconstraint_subclasses():
    """
        A class that returns all the subclasses (recursively) that inherits from TTContraints.

    :return: A set of subclasses

    """
    return all_constraint_subclasses(TTConstraint)


def getTTConstraintsInDB(week, department):
    """
        Returns all classes' instances that inherit from TTConstraint and exist for the given week and department in the database.

    :param week: The week we want to search the TTConstraints that are applied on.
    :param department: The department we want to search the TTConstraints that are applied on.
    :return: A list of TTConstraint's instances.

    """

    # Init
    constraints_list = []
    # Get all the classes that inherit from TTConstraint
    all_constraints_classes = all_TTconstraint_subclasses()

    # Browse for each subclass if we can find an existing instance of this subclass and add it to the list
    for constraint_class in all_constraints_classes:
        try:
            if constraint_class.objects.all().exists():
                all_this_type_constraints = constraint_class.objects.filter(Q(weeks=week)|Q(weeks__isnull=True),
                                                                            department=department,
                                                                            weight=None)
                for constraint in all_this_type_constraints:
                    try:
                        constraints_list.append(constraint)
                    except AttributeError:
                        pass
        except AttributeError:
            pass

    return constraints_list