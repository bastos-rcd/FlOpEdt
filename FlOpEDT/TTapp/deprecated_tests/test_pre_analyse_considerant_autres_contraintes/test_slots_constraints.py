# to fix error message : django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet.
import django
django.setup()
# end
from unittest import skip
from TTapp.deprecated_tests.tools_test_pre_analyse.constraint_test_case import ConstraintTestCase
from base.models import Week, Department
from TTapp.TTConstraints.slots_constraints import ConsiderDependencies


# In this python file we test (class by class) pre_analyse's function for constraints in slots_constraints.py and assert
# the correct result is returned

class ConsiderDependenciesWithConstraintsTestCase(ConstraintTestCase):
    # In this class, we consider the relation between TD and TP as TD has to be given before TP

    fixtures = ['data_test_constraints_with_constraints.json']

    def setUp(self):
        # Set constraint's type
        ConstraintTestCase.setUp(self)
        self.constraint_type = "ConsiderDependencies"

        # Departments
        self.default_dep = Department.objects.get(abbrev="default")

        # Constraints by departments
        self.constraint_default_dep = ConsiderDependencies.objects.get(department=self.default_dep)

        # Weeks
        self.week_40_2022 = Week.objects.get(year=2022, nb=40)
        self.week_41_2022 = Week.objects.get(year=2022, nb=41)
        self.week_42_2022 = Week.objects.get(year=2022, nb=42)
        self.week_43_2022 = Week.objects.get(year=2022, nb=43)
        self.week_44_2022 = Week.objects.get(year=2022, nb=44)
        self.week_45_2022 = Week.objects.get(year=2022, nb=45)

    @skip
    def test_consider_one_tutor_unavailabilities(self):
        # Test 1 : OK case : bibiTU teaches TDdep1 and TDdep2 (both can start only at 10am and 2pm). TDdep1 has to be
        # done before TDdep2 and in the same day. bibiTU is unavailable on tuesdays and wednesdays (NoTutorCourseOnDay),
        # on thursdays and fridays (unavailable user's preference) and on mondays, between 12am and 1pm (TutorLunchBreak).
        # TDdep1 can be given on monday at 10am and TDdep2 can be given at 2pm. It is OK.
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_40_2022)
        self.assertJsonResponseIsOK("1", json_response_dict)

        # Test 2 : KO case : same as Test 1 but TutorLunchBreak is from 11am until 1pm, so TDdep1 and TDdep2 can only be
        # given at the same time : beginning at 2pm, wich is impossible because bibiTU can not teach two courses
        # at the same time.
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_41_2022)
        self.assertJsonResponseIsKO("2", json_response_dict)

