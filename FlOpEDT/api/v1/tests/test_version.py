import pytest

from rest_framework.status import (
    HTTP_406_NOT_ACCEPTABLE,
    HTTP_403_FORBIDDEN,
    is_success,
)
from api.v1.tests.utils import retrieve_elements, add_user_permission

from base.models import EdtVersion


class TestEdtVersion:
    endpoint = "/fr/api/v1/base/courses/version/"

    @pytest.mark.skip("not yet implemented")
    def test_filter_period(self):
        pass

    @pytest.mark.skip("not yet implemented")
    def test_filter_dept(self):
        pass

    def test_perm_everybody_allowed(self, client, make_users):
        min_param = {"from_date": "2024-01-01", "to_date": "2025-01-01"}
        response = client.get(self.endpoint, min_param)
        assert is_success(response.status_code), response.content
        u = make_users(1)[0]
        client.force_authenticate(u)
        response = client.get(self.endpoint, min_param)
        assert is_success(response.status_code)
