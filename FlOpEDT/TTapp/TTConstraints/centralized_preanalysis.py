import django
django.setup()

from TTapp.TTConstraints import *
from TTapp.TTConstraint import TTConstraint
from base.models import Week, Department
from people.models import Tutor

from base.partition import Partition
from django.db.models import Q
from base.models import Course, UserPreference, Holiday
from base.timing import Day, flopdate_to_datetime
from base.timing import TimeInterval
from TTapp.TTConstraints.no_course_constraints import NoCourseOnDay


import TTapp.tests.test_pre_analyse.json_response as json_response_module

def pre_analyse(department, week):
    all_constraints_classes = TTConstraint.__subclasses__()
    #print(all_constraints_classes)
    KO_was_found = False

    for constraint_class in all_constraints_classes:
        try:
            print(constraint_class.objects.all())
            if constraint_class.objects.all().exists():
                print("OK entering ...")
                all_this_type_constraints = constraint_class.objects.filter(Q(department=department) & Q(weeks=week))
                print("remaining:",all_this_type_constraints)
                for constraint in all_this_type_constraints:
                    print(constraint.weeks.all())
                    try:
                        json_dict = constraint.pre_analyse(week)
                        print(json_dict)

                        # KO status found, stop all pre-analysis and return a KO status with a message explaining why
                        if json_response_module.isResponseKO(json_dict):
                            print(type(json_dict))
                            return json_dict
                    except AttributeError:
                        pass
        except AttributeError:
            pass

    # All status returned by all pre-analysis iterations are OK
    json_dict = {"status": "OK", "messages": [], "period": {"week": week.nb, "year": week.year}}
    return json_dict


# TODO : ecrire plus joliment ces 2 fonctions
def all_TTconstraint_subclasses():
    return all_constraint_subclasses(TTConstraint)

def all_constraint_subclasses(class_name):
    constraint_subclasses = set(class_name.__subclasses__())

    if constraint_subclasses != None:
        for subclass in class_name.__subclasses__():
            print(subclass.__name__)
            constraint_subclasses = constraint_subclasses.union(all_constraint_subclasses(subclass))
        return constraint_subclasses

    else:
        return set()

def createPartition(week, department, tutor=None, group=None):
    # Init partition
    partition = Partition.get_partition_of_week(week, department, True)

    constraints_list = []
    all_constraints_classes = all_TTconstraint_subclasses()
    for constraint_class in all_constraints_classes:
        try:
            print(constraint_class.__name__,constraint_class.objects.all())
            if constraint_class.objects.all().exists():
                print("OK entering ...")
                all_this_type_constraints = constraint_class.objects.filter(Q(department=department) & Q(weeks=week))
                print("remaining:",all_this_type_constraints)
                for constraint in all_this_type_constraints:
                    print(constraint.weeks.all())
                    try:
                        constraints_list.append(constraint)
                    except AttributeError:
                        pass
        except AttributeError:
            pass

    for constraint in constraints_list:
        try:
            partition = constraint.complete_partition(partition, tutor, week)
        except AttributeError:
            pass
    # User preferences
    #tutor_partition =

    # NoCourseOnDay constraint : filter department, weeks
    #no_course_on_day = NoCourseOnDay.objects.filter(Q(department=department) &Q(weeks=week))


    #NoTutorCourseOnDay
    return partition



if __name__ == "__main__":
    week = Week.objects.get(year=2022, nb=1)
    default_dep = Department.objects.get(abbrev="default")
    tutor = Tutor.objects.get(username="bibiTU")

    #json_dict = pre_analyse(default_dep,week)
    #print(json_dict)
    print("________________________________________")
    createPartition(week,department=default_dep)


    # TODO : - ecrire les `def complete_partition(self, partition, tutor, week):` dans les TTConstraints ou c'est utile
    #        - permet de completer une partition initiale avec les donnees relatives a un group, un tutor ...etc
    #        - donc faire plusieurs methodes avec des classes differentes ? une pour tutor, une pour group ? (createPartition)
    #        - verifier si en remplacant les bouts de code correspondants dans pre_analyse, ca marche toujours ? exemple : ConsiderTutorUnavailability
    #        - clean code : cf les to do dans no_course_constraints.py