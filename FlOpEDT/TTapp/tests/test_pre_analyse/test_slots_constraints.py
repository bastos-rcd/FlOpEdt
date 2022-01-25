# to fix error message : django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet.
import django
django.setup()
# end
from unittest import skip
from TTapp.tests.test_pre_analyse.constraint_test_case import ConstraintTestCase
from base.models import Week, Department
from TTapp.TTConstraints.slots_constraints import ConsiderDependencies

class ConsiderDependenciesTestCase(ConstraintTestCase):

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
        self.week_7_2022 = Week.objects.get(year=2022, nb=1)

    def test(self):
        # TODO
        # Test 1
        self.assertTrue(True)

# TODO : delete at the end, only print tests
if __name__ == "__main__":
    my_week = Week.objects.get(year=2022, nb=1)
    dep = Department.objects.get(abbrev="Dept2")
    constraint = ConsiderDependencies.objects.get(department=dep)
    dico = constraint.pre_analyse(week=my_week)
    print(dico)
