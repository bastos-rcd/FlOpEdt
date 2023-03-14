#only to solve a bug, maybe to delete
import django
django.setup()
#end

from TTapp.TTConstraints.TTConstraint import TTConstraint
from django.db.models import Q



def pre_analyse(department, week):
    """
        A global pre_analyse function that launch all "pre_analyse" on the existing TTConstraints for the given department and week.

    :param department: The department we want to search the TTConstraints that are applied on.
    :param week: The week we want to search the TTConstraints that are applied on.
    :return: A dictionary with an exit status with a message that contains the reason of why it will be impossible to
    create a timetable with the given data if the status is KO. If this status is KO for one pre_analyse, the loop stops
    and the resulting status is the KO status returned by the one pre_analyse that failed.

    """

    # Get all the classes that inherit from TTConstraint
    all_constraints_classes = TTConstraint.__subclasses__()

    # Search for each TTConstraint's subclass if we can find an instance of it for the given week and department
    result=[]
    for constraint_class in all_constraints_classes:
        try:
            #print(constraint_class.objects.all())
            if constraint_class.objects.exists():
                all_this_type_constraints = constraint_class.objects.filter(Q(weeks=week) | Q(weeks__isnull=True),
                                                                            department=department,
                                                                            weight=None)
                #print("remaining:",all_this_type_constraints)
                for constraint in all_this_type_constraints:
                    #print(constraint.weeks.all())
                    # Try to launch the pre_analyse function (if it exists)
                    try:
                        json_dict = constraint.pre_analyse(week)
                        #print(json_dict)
                        if json_dict['status']!='OK':
                            # KO status found
                            result.append(json_dict)
                    except AttributeError:
                        pass
        except AttributeError:
            pass

    # All status returned by all pre-analysis iterations are OK
    json_dict = {"status": "OK", "messages": [], "period": {"week": week.nb, "year": week.year}}

    return result