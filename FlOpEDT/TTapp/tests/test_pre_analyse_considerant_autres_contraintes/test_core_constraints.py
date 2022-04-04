
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
        # Test 1 : KO case : tutor "bibiTU" has 2 courses of 2h to give but only 2h available in his schedule in first week of 2022
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_20_2022)
        self.assertJsonResponseIsKO("1", json_response_dict)

        # Test 2 : OK case : tutor "bibiTU" has 2 courses of 2h to give and 2 days entirely available in 2nd week
        #json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_3_2022)
        #self.assertJsonResponseIsOK("2", json_response_dict)

