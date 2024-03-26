import pytest
from rest_framework.status import (HTTP_400_BAD_REQUEST, is_success)

from base.models import Department


class TestAllowedStartTimes:
    endpoint = "/fr/api/v1/constraint/base/course_start_time/"

    def test_unknown_dept(self, db, client):
        assert Department.objects.count() == 0
        response = client.get(self.endpoint, {"department_id": 1})
        assert response.status_code == HTTP_400_BAD_REQUEST, response.content

    @pytest.mark.skip("not yet implemented")
    def test_filter_dept(self):
        pass

    def test_perm_read_everybody_allowed(self, client, make_users):
        response = client.get(self.endpoint)
        assert is_success(response.status_code), response.content
        u = make_users(1)[0]
        client.force_authenticate(u)
        response = client.get(self.endpoint)
        assert is_success(response.status_code)
