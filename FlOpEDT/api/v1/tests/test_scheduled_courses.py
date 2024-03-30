# Tests use to unuse arguments...
# pylint: disable=unused-argument

import pytest
from rest_framework.status import (
    HTTP_403_FORBIDDEN,
    HTTP_406_NOT_ACCEPTABLE,
    is_success,
)

from api.v1.tests.utils import add_user_permission, retrieve_elements
from base.models import Course, StructuralGroup


class TestScheduledCourseArrange:
    def test_fixture(self, make_courses):
        assert Course.objects.count() == (2**3 - 1) * 2, Course.objects.all()

        cms = StructuralGroup.objects.filter(parent_groups__isnull=True)
        tps = StructuralGroup.objects.filter(basic=True)
        tds = set(StructuralGroup.objects.all()) - set(cms) - set(tps)
        assert len(cms) == 1 and len(tds) == 2 and len(tps) == 4

        assert len([c for c in Course.objects.all() if c.groups.count() != 1]) == 0

        n = 2
        assert len(Course.objects.filter(groups__in=cms)) == 2**0 * n
        assert len(Course.objects.filter(groups__in=tds)) == 2**1 * n
        assert len(Course.objects.filter(groups__in=tps)) == 2**2 * n

        for gp in StructuralGroup.objects.all():
            assert (
                len(Course.objects.filter(groups__in=[gp])) == n
            ), Course.objects.filter(groups__in=[gp])


class TestScheduledCourseList:
    endpoint = "/fr/api/v1/base/courses/scheduled_courses"
