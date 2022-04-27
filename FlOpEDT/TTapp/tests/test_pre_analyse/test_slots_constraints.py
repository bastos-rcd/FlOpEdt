# to fix error message : django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet.
import django
django.setup()
# end
from TTapp.tests.tools_test_pre_analyse.constraint_test_case import ConstraintTestCase
from base.models import Week, Department
from TTapp.TTConstraints.slots_constraints import ConsiderDependencies, SimultaneousCourses


# In this python file we test (class by class) pre_analyse's function for constraints in slots_constraints.py and assert
# the correct result is returned

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
        self.week_19_2022 = Week.objects.get(year=2022, nb=19)
        self.week_20_2022 = Week.objects.get(year=2022, nb=20)


    def test_OK_case(self):
        # Test 1 : OK case : "bibiTU" has one TD and one TP to do (which last 2 hours and 1h30), they must be successive
        #          and "bibiTU" is only available on wednesday between 6 and 10 o'clock am,
        #          TD must start at 6 am and TP must start at 8 am, it is OK.
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_13_2022)
        self.assertJsonResponseIsOK("1", json_response_dict)

        # Test 2 : OK case : "bibiTU" has one TD and one TP to do (which last 2 hours and 1h30), they must be done in the same day
        #          and "bibiTU" is only available on wednesday between 8 and 10 o'clock am and between 2 and 4 o'clock pm,
        #          TD must start at 8 am and TP must start at 2 pm, it is OK.
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_14_2022)
        self.assertJsonResponseIsOK("2", json_response_dict)

        # Test 3 : OK case : "bibiTU" has one TD and one TP to do (which last 2 hours and 1h30), they must be done on different days
        #          and "bibiTU" is only available on wednesday between 8 and 10 o'clock am and thursday between 2 and 4 o'clock pm,
        #          TD must start at 8 am and TP must start at 2 pm, it is OK.
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_15_2022)
        self.assertJsonResponseIsOK("3", json_response_dict)

    def test_consider_tutors_unavailabilities(self):
        # Test 4 : KO case : "bibiTU" has one TD to give and "Prof1" has one TP to give,
        #          "bibiTU" is only unavailable on monday and "Prof1" is only available on monday,
        #          as TD must be given before TP, and considering tutors' unavailabilities, TD can not be done before TP.
        json_response_dict = self.constraint_dep_2.pre_analyse(week=self.week_17_2022)
        self.assertJsonResponseIsKO("4", json_response_dict)

    def test_consider_courses_beginning_time(self):
        # Test 5 : KO case : Tutor "bibiTU" has a TD and TP to give (which last 2 hours and 1h30) and he is only available
        #          on monday afternoon and on tuesday, wednesday, thursday, friday mornings,
        #          TD must start at 8 am and TP must start at 2 pm,
        #          so "bibiTU" can not assure TD before TP.
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_16_2022)
        self.assertJsonResponseIsKO("5", json_response_dict)

    def test_consider_supp_tutors_unavailabilities(self):
        # Test 6 : KO case : Tutor "bibiTU" has a TD and TP to give and he is available every day but monday
        #          (when he is available only between 6 o'clock pm and 8 o'clock pm) and tutor "Prof1" is supp_tutor for
        #          TP but he is only available on monday. So TP can not be ensured by "Prof1" before TD.
        json_response_dict = self.constraint_dep_2.pre_analyse(week=self.week_18_2022)
        self.assertJsonResponseIsKO("6", json_response_dict)

        # Test 7 : KO case : TD has to be done before TP and there are 3 supp tutors : "bibiTU" and "Prof1" are always
        #          available but "Prof2" is only available on monday, tuesday, wednesday and thursday afternoons
        #          and on friday mornings but the TD can only start at 8 o'clock am and TP can only start at 2 o'clock pm,
        #          so "Prof2" can not handle the 2 courses with this dependency.
        json_response_dict = self.constraint_dep_2.pre_analyse(week=self.week_20_2022)
        self.assertJsonResponseIsKO("7", json_response_dict)


    def test_consider_NoTutorCourseOnDay_constraints(self):
        # Test 8 : KO case : TD6 has to be done before TD7, "bibiTU" and "Prof1" are the supp tutors for TD6,
        #          "bibiTU" and "Prof2" are the supp tutors for TD7, "bibiTU" can handle the 2 courses
        #          (available thursday and friday), even with the dependency, "Prof1" has all slots available
        #          but "Prof2" has forbidden slots everywhere, because of supp tutors unavailabilities,
        #          the 2 courses can not be done one after another.
        json_response_dict = self.constraint_dep_2.pre_analyse(week=self.week_19_2022)
        self.assertJsonResponseIsKO("8", json_response_dict)

class SimultaneousCoursesTestCase(ConstraintTestCase):

    fixtures = ['data_test_constraints_SimultaneousCourses.json']

    def setUp(self):
        # Set constraint's type
        ConstraintTestCase.setUp(self)
        self.constraint_type = "SimultaneousCourses"

        # Departments
        self.default_dep = Department.objects.get(abbrev="default")

        # Constraints by departments
        self.constraint_default_dep = ConsiderDependencies.objects.get(department=self.default_dep)

        # Weeks
        self.week_1_2022 = Week.objects.get(year=2022, nb=1)
        self.week_2_2022 = Week.objects.get(year=2022, nb=2)



    def test_OK_case(self):
        # Test 1 : OK case : Many groups/tutors doing courses simultaneously
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_1_2022)
        self.assertJsonResponseIsOK("1", json_response_dict)

    def test_KO_case(self):
        # Test 2 : KO case : Tutor(s) doing more than one course simultaneously
        #                    Group(s) doing more than one course simultaneously
        #                    No common time for courses to be done simultaneously
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_1_2022)
        self.assertJsonResponseIsKO("2", json_response_dict)

