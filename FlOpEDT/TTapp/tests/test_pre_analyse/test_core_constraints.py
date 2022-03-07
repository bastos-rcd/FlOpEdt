
# to fix error message : django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet.
import django
django.setup()
# end
from unittest import skip
from TTapp.tests.test_pre_analyse.constraint_test_case import ConstraintTestCase
from base.models import Week, Department
from TTapp.TTConstraints.core_constraints import ConsiderTutorsUnavailability, NoSimultaneousGroupCourses

# In this python file we test (class by class) pre_analyse's function for constraints in core_constraints.py and assert
# the correct result is returned

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
        # Test 1 : KO case : group TD2 has 3 TD courses of 2 hours to do in the week, but TD course can only start
        #          friday at 8:00 am, so only one course can be placed, there are not enough slots.
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_7_2022)
        self.assertJsonResponseIsKO("1", json_response_dict)

        # Test 2 : OK case : group TD2 has 2 TD courses of 2 hours to do in the week and there are 2 slots of 2 hours available.
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_8_2022)
        self.assertJsonResponseIsOK("2", json_response_dict)

    def test_consider_no_simultaneous_groups_and_subgroups_courses(self):
        # Test 3 : KO case : group TD2 has a TD course of 2 hours to do in the week and its subgroup TP2A has a TP course
        #          of 2 hours to do, but TD course and TP course can both only begin at 8:00 am on friday.
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_9_2022)
        self.assertJsonResponseIsKO("3", json_response_dict)

        # Test 4 : OK case : group TD2 has a TD course of 2 hours to do and its two subgroups TP2A and TP2B have both
        #          a TP course of 2 hours to do, TD course can begin on wednesday at 8:00 am and TP courses can begin
        #          on friday at 8:00 am, there is no conflict.
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_10_2022)
        self.assertJsonResponseIsOK("4", json_response_dict)

        # Test 5 : KO case : same as test 3 but the group TD2 has a subgroup with the same type, TD21.
        json_response_dict = self.constraint_dep_2.pre_analyse(week=self.week_9_2022)
        self.assertJsonResponseIsKO("5", json_response_dict)

        # Test 6 : OK case : same as test 4 but the group TD2 has two subgroups with the same type, TD21 and TD22.
        json_response_dict = self.constraint_dep_2.pre_analyse(week=self.week_10_2022)
        self.assertJsonResponseIsOK("6", json_response_dict)

    def test_consider_transversal_courses(self):
        # Test 7 : KO case : groups TD1 and TD2 have a transversal group TD3, those three groups have each one TD course
        #          of 2 hours to do but the only slot available for the 3 TD courses is on friday at 8:00 am.
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_11_2022)
        self.assertJsonResponseIsKO("7", json_response_dict)

        # Test 8 : OK case : groups TD1 and TD2 have a transversal group TD3, those three groups have each one TD course
        #          of 2 hours to do and two slots are available for the 3 TD courses, on friday at 8:00 am and on wednesday
        #          at 8:00 am.
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_12_2022)
        self.assertJsonResponseIsOK("8", json_response_dict)

