import pytest
from rest_framework.status import (
    HTTP_403_FORBIDDEN,
    HTTP_406_NOT_ACCEPTABLE,
    is_success,
)

from api.v1.tests.utils import add_user_permission, retrieve_elements
from base.models import Module


class TestScheduledCourseList:
    endpoint = "/fr/api/v1/base/courses/scheduled_courses"

    @pytest.mark.skip("Not yet implemented")
    def test_dept_filter(self, client):
        pass

    @pytest.mark.skip("Not yet implemented")
    def test_dept_and_tp_filter_fail(self, client):
        pass

    @pytest.mark.skip("Not yet implemented")
    def test_dept_and_tp_filter_success(self, client):
        pass

    @pytest.mark.skip("Not yet implemented")
    def test_perm_change_denied(self, client):
        pass
