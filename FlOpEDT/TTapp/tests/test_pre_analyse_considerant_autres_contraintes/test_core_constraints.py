
# to fix error message : django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet.
import django
django.setup()
# end
from TTapp.tests.tools_test_pre_analyse.constraint_test_case import ConstraintTestCase
from base.models import Week, Department
from TTapp.TTConstraints.core_constraints import ConsiderTutorsUnavailability, NoSimultaneousGroupCourses

# In this python file we test (class by class) pre_analyse's function for constraints in core_constraints.py and assert
# the correct result is returned

class ConsiderTutorsUnavailabilityWithConstraintsTestCase(ConstraintTestCase):

    fixtures = ['data_test_constraints_with_constraints.json']

    def setUp(self):
        # Set constraint's type
        ConstraintTestCase.setUp(self)
        self.constraint_type = "ConsiderTutorsUnavailability"

        # Departments
        self.default_dep = Department.objects.get(abbrev="default")

        # Constraints by departments
        self.constraint_default_dep = ConsiderTutorsUnavailability.objects.get(department=self.default_dep)

        # Weeks
        self.week_20_2022 = Week.objects.get(year=2022, nb=20)
        self.week_21_2022 = Week.objects.get(year=2022, nb=21)
        self.week_22_2022 = Week.objects.get(year=2022, nb=22)
        self.week_23_2022 = Week.objects.get(year=2022, nb=23)
        self.week_24_2022 = Week.objects.get(year=2022, nb=24)
        self.week_25_2022 = Week.objects.get(year=2022, nb=25)

    def test_consider_unavailabilities_lunch_break_and_no_course(self):
        # Test 1 : KO case : Tutor lunch breaks are on mondays, wednesdays and fridays (from 11:00 am until 3:00 pm),
        #          no tutor course on tuesday and tutor "bibiTU" unavailable all thursdays and on monday's, wednesday's
        #          and friday's morning (from 6:00 am until 10:00 am). "bibiTU" has 2 courses of 2h to give and both can
        #          start at 8:00 am or 10:00 am, impossible to schedule.
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_20_2022)
        self.assertJsonResponseIsKO("1", json_response_dict)

        # Test 2 : OK case : Tutor lunch breaks on tuesdays and wednesdays, no tutor course on thursdays and fridays,
        #          tutor unavailable on monday and on wednesday's morning. "bibiTU" has 1 course to give of 2h that can
        #          start at 8:00 am or 10:00 am. The course can be done tuesday morning, it is ok.
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_22_2022)
        self.assertJsonResponseIsOK("2", json_response_dict)

        # Test 3 : KO case : Same as test 2 but "bibiTU" has 2 courses of 2h to give, which is impossible.
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_23_2022)
        self.assertJsonResponseIsKO("3", json_response_dict)



class NoSimultaneousGroupCoursesWithConstraintsTestCase(ConstraintTestCase):

    fixtures = ['data_test_constraints_with_constraints.json']

    def setUp(self):
        # Set constraint's type
        ConstraintTestCase.setUp(self)
        self.constraint_type = "NoSimultaneousGroupCourses"

        # Departments
        self.default_dep = Department.objects.get(abbrev="default")

        # Constraints by departments
        self.constraint_default_dep = NoSimultaneousGroupCourses.objects.get(department=self.default_dep)

        # Weeks
        self.week_30_2022 = Week.objects.get(year=2022, nb=30)
        self.week_31_2022 = Week.objects.get(year=2022, nb=31)


    def test_consider_group_lunch_break(self):
        # Test 1 : OK case : .
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_20_2022)
        self.assertJsonResponseIsKO("1", json_response_dict)

        # Test 2 : KO case : .
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_21_2022)
        self.assertJsonResponseIsOK("2", json_response_dict)
