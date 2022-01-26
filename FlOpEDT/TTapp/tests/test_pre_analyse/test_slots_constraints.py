# to fix error message : django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet.
import django
django.setup()
# end
from unittest import skip
from TTapp.tests.test_pre_analyse.constraint_test_case import ConstraintTestCase
from base.models import Week, Department
from TTapp.TTConstraints.slots_constraints import ConsiderDependencies

class ConsiderDependenciesTestCase(ConstraintTestCase):
    # In this class, we consider the relation between TD and TP as TD has to be given before TP

    fixtures = ['data_test_constraints.json']

    def setUp(self):
        # Set constraint's type
        ConstraintTestCase.setUp(self)
        self.constraint_type = "ConsiderDependencies"

        # Departments
        self.default_dep = Department.objects.get(abbrev="default")
        self.dep_2 = Department.objects.get(abbrev="Dept2")

        # Constraints by departments
        self.constraint_default_dep = ConsiderDependencies.objects.get(department=self.default_dep)
        self.constraint_dep_2 = ConsiderDependencies.objects.get(department=self.dep_2)

        # Weeks
        self.week_13_2022 = Week.objects.get(year=2022, nb=13)
        self.week_14_2022 = Week.objects.get(year=2022, nb=14)
        self.week_15_2022 = Week.objects.get(year=2022, nb=15)
        self.week_16_2022 = Week.objects.get(year=2022, nb=16)
        self.week_17_2022 = Week.objects.get(year=2022, nb=17)
        self.week_18_2022 = Week.objects.get(year=2022, nb=18)



    def test_OK_case(self):
        # TODO
        # Test 1 : OK case
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_13_2022)
        self.assertJsonResponseIsOK("1", json_response_dict)
        # Test 2 : OK case
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_14_2022)
        self.assertJsonResponseIsOK("2", json_response_dict)
        # Test 3 : OK case
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_15_2022)
        self.assertJsonResponseIsOK("3", json_response_dict)

    def test_consider_tutors_unavailabilities(self):
        # Test 4 : KO case
        json_response_dict = self.constraint_dep_2.pre_analyse(week=self.week_17_2022)
        self.assertJsonResponseIsKO("4", json_response_dict)

    def test_consider_courses_beginning_time(self):
        # Test 5 : KO case
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_16_2022)
        self.assertJsonResponseIsKO("5", json_response_dict)

    def test_consider_supp_tutors_unavailabilities(self):
        # Test 6 : KO case : Tutor "bibiTU" has a TD and TP to give and he is available every day but monday
        #          (when he is available only between 6 o'clock pm and 8 o'clock pm) and tutor "Prof1" is supp_tutor for
        #          TP but he is only available on monday. So TP can not be ensured by "Prof1" before TD.
        json_response_dict = self.constraint_dep_2.pre_analyse(week=self.week_18_2022)
        self.assertJsonResponseIsKO("6", json_response_dict)

# TODO : delete at the end, only print tests
if __name__ == "__main__":
    my_week = Week.objects.get(year=2022, nb=18)
    # Departments
    default_dep = Department.objects.get(abbrev="default")
    dep_2 = Department.objects.get(abbrev="Dept2")

    # Constraints by departments
    constraint_default_dep = ConsiderDependencies.objects.get(department=default_dep)
    constraint_dep_2 = ConsiderDependencies.objects.get(department=dep_2)

    dico = constraint_dep_2.pre_analyse(my_week)
    print(dico)

    #dep = Department.objects.get(abbrev="Dept2")
    #constraint = ConsiderDependencies.objects.get(department=dep)
    #dico = constraint.pre_analyse(week=my_week)
    #constraints = ConsiderDependencies.objects.all()
    #for c in constraints:
    #    dico = c.pre_analyse(week=my_week)
    #    print(dico)
    #    print(dep)
