# to fix error message : django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet.
import django

django.setup()
# end
from unittest import skip

from base.models import Department, Week
from TTapp.deprecated_tests.tools_test_pre_analyse.constraint_test_case import (
    ConstraintTestCase,
)
from TTapp.TimetableConstraints.core_constraints import (
    ConsiderTutorsUnavailability,
    NoSimultaneousGroupCourses,
)

# In this python file we test (class by class) pre_analyse's function for constraints in core_constraints.py and assert
# the correct result is returned


class ConsiderTutorsUnavailabilityWithConstraintsTestCase(ConstraintTestCase):
    fixtures = ["data_test_constraints_with_constraints.json"]

    def setUp(self):
        # Set constraint's type
        ConstraintTestCase.setUp(self)
        self.constraint_type = "ConsiderTutorsUnavailability"

        # Departments
        self.default_dep = Department.objects.get(abbrev="default")

        # Constraints by departments
        self.constraint_default_dep = ConsiderTutorsUnavailability.objects.get(
            department=self.default_dep
        )

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
        json_response_dict = self.constraint_default_dep.pre_analyse(
            week=self.week_20_2022
        )
        self.assertJsonResponseIsKO("1", json_response_dict)

        # Test 2 : OK case : Tutor lunch breaks on tuesdays and wednesdays, no tutor course on thursdays and fridays,
        #          tutor unavailable on monday and on wednesday's morning. "bibiTU" has 1 course to give of 2h that can
        #          start at 8:00 am or 10:00 am. The course can be done tuesday morning, it is ok.
        json_response_dict = self.constraint_default_dep.pre_analyse(
            week=self.week_22_2022
        )
        self.assertJsonResponseIsOK("2", json_response_dict)

        # Test 3 : KO case : Same as test 2 but "bibiTU" has 2 courses of 2h to give, which is impossible.
        json_response_dict = self.constraint_default_dep.pre_analyse(
            week=self.week_23_2022
        )
        self.assertJsonResponseIsKO("3", json_response_dict)


class NoSimultaneousGroupCoursesWithConstraintsTestCase(ConstraintTestCase):
    fixtures = ["data_test_constraints_with_constraints.json"]

    def setUp(self):
        # Set constraint's type
        ConstraintTestCase.setUp(self)
        self.constraint_type = "NoSimultaneousGroupCourses"

        # Departments
        self.default_dep = Department.objects.get(abbrev="default")

        # Constraints by departments
        self.constraint_default_dep = NoSimultaneousGroupCourses.objects.get(
            department=self.default_dep
        )

        # Weeks
        self.week_30_2022 = Week.objects.get(year=2022, nb=30)
        self.week_31_2022 = Week.objects.get(year=2022, nb=31)
        self.week_32_2022 = Week.objects.get(year=2022, nb=32)
        self.week_33_2022 = Week.objects.get(year=2022, nb=33)
        self.week_34_2022 = Week.objects.get(year=2022, nb=34)
        self.week_35_2022 = Week.objects.get(year=2022, nb=35)

    def test_consider_GroupLunchBreak(self):
        # Test 1 : OK case : Group "TD1info" has two courses of 2 hours that can only start at 10am to follow, but there are 3
        # NoGroupCourseOnDay's constraints on tuesday, wednesday and thursday and the group has a lunch break from
        # 12am until 2pm on friday. One course can be given on monday and another on friday, it is OK.
        json_response_dict = self.constraint_default_dep.pre_analyse(
            week=self.week_30_2022
        )
        self.assertJsonResponseIsOK("1", json_response_dict)

        # Test 2 : KO case : Same as Test 1 but the friday's lunch break is now from 11am until 2pm,
        # the second course can not be given on friday, because of its duration (2 hours).
        json_response_dict = self.constraint_default_dep.pre_analyse(
            week=self.week_31_2022
        )
        self.assertJsonResponseIsKO("2", json_response_dict)

    @skip
    def test_transversal_groups(self):
        # Test 3 : OK case : TD1, TD2 and a transversal group between TD1 and TD2 have all one course (starting at 10am) to do.
        # TD1 and TD2 has NoGroupCourseOnDay on thursday and TD2 on monday. All GroupLunchBreak begin at
        # 11am and end at 2pm. TD1 has a lunch break on tuesday and wednesday. TD2 has a lunch break on wednesday.
        # TD1's course can be done on monday, TD2's on tuesday and transversal group's course can be done on friday.
        json_response_dict = self.constraint_default_dep.pre_analyse(
            week=self.week_32_2022
        )
        self.assertJsonResponseIsOK("3", json_response_dict)

        # Test 4 : KO case : Same as Test 3 but GroupLunchBreak on friday for the two groups, no slot available for
        # the transversal group's course.
        json_response_dict = self.constraint_default_dep.pre_analyse(
            week=self.week_33_2022
        )
        self.assertJsonResponseIsKO("4", json_response_dict)

    def test_transversal_groups_and_subgroups(self):
        # Test 5 : OK case : GroupLunchBreak on monday and tuesday from 11am until 2pm.
        # Group TD1 has one course to follow and has two subgroups TP1 and TP2 which have both one course to follow.
        # Group TD2 has one course to follow and a transversal group of TD1 and TD2 has one course to follow.
        # All courses can only begin at 10am. So no course on monday and tuesday, TD1 and TD2 can have a course on wednesday,
        # TP1 and TP2 on thursday, and the transversal group can have a course on friday. It is OK.
        json_response_dict = self.constraint_default_dep.pre_analyse(
            week=self.week_34_2022
        )
        self.assertJsonResponseIsOK("5", json_response_dict)

        # Test 6 : KO case : Same as Test 5 but with a GroupLunchBreak on wednesday from 11am until 2pm, so one available
        # slot is not available anymore, it is impossible to schedule all courses in the week.
        json_response_dict = self.constraint_default_dep.pre_analyse(
            week=self.week_35_2022
        )
        self.assertJsonResponseIsKO("6", json_response_dict)
