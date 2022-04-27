import django
django.setup()

from TTapp.TTConstraints.TTConstraint import TTConstraint

from base.models import Week, Department

from django.db.models import Q
from TTapp.TTConstraints.core_constraints import NoSimultaneousGroupCourses, ConsiderTutorsUnavailability
from TTapp.TTConstraints.slots_constraints import ConsiderTutorUnavaibility, SimultaneousCourses
import TTapp.tests.tools_test_pre_analyse.json_response as json_response_module

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






if __name__ == "__main__":

    #week = Week.objects.get(year=2022, nb=1)
    #default_dep = Department.objects.get(abbrev="default")
    #tutor = Tutor.objects.get(username="bibiTU")

    # Departments
    default_dep = Department.objects.get(abbrev="default")

    # Constraints by departments
    constraint_default_dep = ConsiderTutorsUnavailability.objects.get(department=default_dep)

    # Weeks
    week_10_2022 = Week.objects.get(year=2022, nb=20)

    json_dict = constraint_default_dep.pre_analyse(week=week_10_2022)
    print(json_dict)
    #print(json_dict)
    #print("________________________________________")
    #createPartition(week,department=default_dep)


    # TODO : - ecrire les `def complete_partition(self, partition, tutor, week):` dans les TTConstraints ou c'est utile
    #        - permet de completer une partition initiale avec les donnees relatives a un group, un tutor ...etc
    #        - donc faire plusieurs methodes avec des classes differentes ? une pour tutor, une pour group ? (createPartition)
    #        - verifier si en remplacant les bouts de code correspondants dans pre_analyse, ca marche toujours ? exemple : ConsiderTutorUnavailability
    #        - clean code : cf les to do dans no_course_constraints.py