from TTapp.FlopConstraint import FlopConstraint
from TTapp.FlopConstraint import all_subclasses
from django.db.models import Q


def getFlopConstraintsInDB(period, department):
    """
        Returns all classes' instances that inherit from TTConstraint and exist for the given period and department in the database.

    :param period: The scheduling period we want to search the TTConstraints that are applied on.
    :param department: The department we want to search the TTConstraints that are applied on.
    :return: A list of TTConstraint's instances.

    """

    # Init
    constraints_list = []
    # Get all the classes that inherit from TTConstraint
    all_constraints_classes = all_subclasses(FlopConstraint)

    # Browse for each subclass if we can find an existing instance of this subclass and add it to the list
    for constraint_class in all_constraints_classes:
            if constraint_class.objects.all().exists():
                all_this_type_constraints = constraint_class.objects.filter(Q(periods=period)|Q(periods__isnull=True),
                                                                            department=department,
                                                                            weight=None,
                                                                            is_active=True)
                for constraint in all_this_type_constraints:
                    constraints_list.append(constraint)

    return constraints_list
