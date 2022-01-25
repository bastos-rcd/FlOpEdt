
# to fix error message : django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet.
import django
django.setup()
# end
from unittest import skip
from TTapp.tests.test_pre_analyse.constraint_test_case import ConstraintTestCase
from base.models import Week, Department
from TTapp.TTConstraints.core_constraints import ConsiderTutorsUnavailability, NoSimultaneousGroupCourses

# Test pre_analyse function for constraints in core_constraints.py : assert correct result returned
class ConsiderTutorsUnavailabilityTestCase(ConstraintTestCase):

    fixtures = ['data_test_constraints.json']

    def setUp(self):
        # Set constraint's type
        ConstraintTestCase.setUp(self)
        self.constraint_type = "ConsiderTutorsUnavailability"

        # Departments
        self.default_dep = Department.objects.get(abbrev="default")
        self.dep_2 = Department.objects.get(abbrev="Dept2")

        # Constraints by departments
        self.constraint_default_dep = ConsiderTutorsUnavailability.objects.get(department=self.default_dep)
        self.constraint_dep_2 = ConsiderTutorsUnavailability.objects.get(department=self.dep_2)

        # Weeks
        self.week_1_2022 = Week.objects.get(year=2022, nb=1)
        self.week_2_2022 = Week.objects.get(year=2022, nb=2)
        self.week_3_2022 = Week.objects.get(year=2022, nb=3)
        self.week_4_2022 = Week.objects.get(year=2022, nb=4)
        self.week_5_2022 = Week.objects.get(year=2022, nb=5)
        self.week_6_2022 = Week.objects.get(year=2022, nb=6)

    def test_consider_tutor_unavailability(self):
        # Test 1 : KO case : tutor "bibiTU" has 2 courses of 2h to give but only 2h available in his schedule in first week of 2022
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_1_2022)
        self.assertJsonResponseIsKO("1", json_response_dict)

        # Test 2 : OK case : tutor "bibiTU" has 2 courses of 2h to give and 2 days entirely available in 2nd week
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_3_2022)
        self.assertJsonResponseIsOK("2", json_response_dict)

    def test_consider_course_beginning_time(self):
        # Test 3 : KO case : tutor "bibiTU" has 2 courses of 2h to give and only 1 day available in 3rd week.
        #          Both courses must begin at 8o'clock wich implies conflicts.
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_2_2022)
        self.assertJsonResponseIsKO("3", json_response_dict)

    def test_consider_holidays(self):
        # Test 4 : KO case : tutor "prof1" has 4 courses to give, all must begin at 8 o'clock, he does not work on mondays
        #          and wednesday is holiday wich implies conflicts
        json_response_dict = self.constraint_dep_2.pre_analyse(week=self.week_2_2022)
        self.assertJsonResponseIsKO("4", json_response_dict)

        # Test 5 : OK case : tutor "prof1" has 3 courses to give, all must begin at 8 o'clock, he does not work on mondays
        #          and wednesday is holiday
        json_response_dict = self.constraint_dep_2.pre_analyse(week=self.week_3_2022)
        self.assertJsonResponseIsOK("5", json_response_dict)

    def test_consider_tutor_unavailability_in_all_departments(self):
        # Test 6 : KO case : tutor "bibiTU" can work only on tuesday and has 2 courses to give, 1 in each department,
        #          but both can begin only at 8 o'clock, wich lead to a conflict.
        json_response_dict_default_dep = self.constraint_default_dep.pre_analyse(week=self.week_4_2022)
        json_response_dict_dep_2 = self.constraint_dep_2.pre_analyse(week=self.week_4_2022)
        self.assertJsonResponseIsKO("6.1", json_response_dict_default_dep) \
        and self.assertJsonResponseIsKO("6.2", json_response_dict_dep_2)

        # Test 7 : OK case : tutor "bibiTU" can work only on tuesday and thursay and has 2 courses to give, 1 in each department,
        #          both can begin only at 8 o'clock
        json_response_dict_default_dep = self.constraint_default_dep.pre_analyse(week=self.week_6_2022)
        json_response_dict_dep_2 = self.constraint_dep_2.pre_analyse(week=self.week_6_2022)
        self.assertJsonResponseIsOK("7.1", json_response_dict_default_dep) \
        and self.assertJsonResponseIsOK("7.2", json_response_dict_dep_2)

    def test_consider_enough_nb_slots(self):
        # Test 8 : KO case : tutor "bibiTU" works only on tuesday, and has 2 courses to give, they must begin at 8 o'clock
        #          wich is impossible.
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_5_2022)
        self.assertJsonResponseIsKO("8", json_response_dict)

    def test_consider_forbidden_days(self):
        # Test 9 : KO case : tutor "prof1" can not work on monday (forbidden day) and he must give 5 courses
        #          that must begin at 8 o'clock
        json_response_dict = self.constraint_dep_2.pre_analyse(week=self.week_1_2022)
        self.assertJsonResponseIsKO("9", json_response_dict)

        # Test 10 : OK case : tutor "prof1" can not work on monday (forbidden day) and he must give 4 courses
        #           that must begin at 8 o'clock
        json_response_dict = self.constraint_dep_2.pre_analyse(week=self.week_5_2022)
        self.assertJsonResponseIsOK("10", json_response_dict)


class NoSimultaneousGroupCoursesTestCase(ConstraintTestCase):
    # TODO : complete

    fixtures = ['data_test_constraints.json']

    def setUp(self):
        # Set constraint's type
        ConstraintTestCase.setUp(self)
        self.constraint_type = "NoSimultaneousGroupCourses"

        # Departments
        self.default_dep = Department.objects.get(abbrev="default")
        self.dep_2 = Department.objects.get(abbrev="Dept2")

        # Constraints by departments
        self.constraint_default_dep = NoSimultaneousGroupCourses.objects.get(department=self.default_dep)
        self.constraint_dep_2 = NoSimultaneousGroupCourses.objects.get(department=self.dep_2)

        # Weeks
        self.week_7_2022 = Week.objects.get(year=2022, nb=7)
        self.week_8_2022 = Week.objects.get(year=2022, nb=8)
        self.week_9_2022 = Week.objects.get(year=2022, nb=9)
        self.week_10_2022 = Week.objects.get(year=2022, nb=10)
        self.week_11_2022 = Week.objects.get(year=2022, nb=11)
        self.week_12_2022 = Week.objects.get(year=2022, nb=12)


    def test_consider_enough_slots_and_time(self):
        # TODO
        # Test 1 : KO case
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_7_2022)
        self.assertJsonResponseIsKO("1", json_response_dict)

        # Test 2 : OK case
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_8_2022)
        self.assertJsonResponseIsOK("2", json_response_dict)

    def test_consider_no_simultaneous_groups_and_subgroups_courses(self):
        # TODO
        # Test 3 : KO case
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_9_2022)
        self.assertJsonResponseIsKO("3", json_response_dict)

        # Test 4 : OK case
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_10_2022)
        self.assertJsonResponseIsOK("4", json_response_dict)

    def test_consider_transversal_courses(self):
        # Test 5 : KO case
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_11_2022)
        self.assertJsonResponseIsKO("5", json_response_dict)

        # Test 6 : OK case
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_12_2022)
        self.assertJsonResponseIsOK("6", json_response_dict)

# TODO : delete at the end, only print tests
if __name__ == "__main__":
    tc = ConsiderTutorsUnavailabilityTestCase()
    # holidays
    my_week = Week.objects.get(year=2022, nb=2)
    dep = Department.objects.get(abbrev="Dept2")
    print(dep)
    constraint_holidays = ConsiderTutorsUnavailability.objects.get(department=dep)
    print(constraint_holidays)
    constraint_holidays.pre_analyse(week=my_week)
    # end holidays
    #tc.assertTrue(False, tc.unexpectedResponseErrorMessage("3", "KO", "OK"))
    #tc.assertTrue(False, tc.constraintNotInJsonResponseErrorMessage("3"))
    '''cs = ConsiderTutorsUnavailability.objects.all()
    my_week = Week.objects.get(year=2022, nb=2)
    print(Department.objects.all())
    dep = list(map(lambda dep: dep.abbrev, Department.objects.all()))
    for dep_abbrev in dep:
        for c in cs:
            if c.department.abbrev == dep_abbrev:
                print("## DEP :", c.department)
                json_response_dict = c.pre_analyse(week=my_week)
                print(json_response_dict)

                jrobject = json_response_module.JsonResponse()
                types = list(map(lambda dico: dico["type"], json_response_dict["messages"]))
                print("## TYPES :",types)
'''
