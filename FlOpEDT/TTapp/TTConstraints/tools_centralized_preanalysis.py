from TTapp.TTConstraint import TTConstraint
from django.db.models import Q


# TODO : move ?
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


# TODO : move ?
def all_TTconstraint_subclasses():
    """
        A class that returns all the subclasses (recursively) that inherits from TTContraints.

    :return: A set of subclasses

    """
    return all_constraint_subclasses(TTConstraint)

# TODO : move ?
def getTTConstraintsInDB(week, department):

    constraints_list = []
    all_constraints_classes = all_TTconstraint_subclasses()

    for constraint_class in all_constraints_classes:
        try:
            #print(constraint_class.__name__, constraint_class.objects.filter(Q(weeks=week)))
            if constraint_class.objects.all().exists():
                print("OK entering ...")
                all_this_type_constraints = constraint_class.objects.filter(
                    Q(department=department) & Q(weeks=week))
                print("remaining:", all_this_type_constraints)
                for constraint in all_this_type_constraints:
                    #print(constraint.weeks.all())
                    try:
                        constraints_list.append(constraint)
                    except AttributeError:
                        pass
        except AttributeError:
            pass

    return constraints_list