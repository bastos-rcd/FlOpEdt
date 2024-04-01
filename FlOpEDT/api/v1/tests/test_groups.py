# Tests use to unuse arguments...
# pylint: disable=unused-argument

from rest_framework.status import (
    HTTP_403_FORBIDDEN,
    is_success,
)

from api.v1.tests.utils import add_user_permission
from base.models import Department
from people.models import User


class TestDepartment:
    endpoint = "/fr/api/v1/base/groups/department/"

    def test_perm_read_allowed(self, db, client):
        response = client.get(self.endpoint)
        assert is_success(response.status_code), response.content
        u = User.objects.create(username="u")
        client.force_authenticate(u)
        response = client.get(self.endpoint)
        assert is_success(response.status_code), response.content

    def test_perm_delete(self, db, client, make_perm_delete_department):
        d = Department.objects.create(abbrev="dpt")
        response = client.delete(f"{self.endpoint}{d.id}/")
        assert response.status_code == HTTP_403_FORBIDDEN, response.content
        u = User.objects.create(username="u")
        client.force_authenticate(u)
        response = client.delete(f"{self.endpoint}{d.id}/")
        assert response.status_code == HTTP_403_FORBIDDEN, response.content
        add_user_permission(u, make_perm_delete_department)
        response = client.delete(f"{self.endpoint}{d.id}/")
        assert is_success(response.status_code), response.content

    def test_perm_add(self, db, client, make_perm_add_department):
        data = {"abbrev": "dept", "name": "department"}
        response = client.post(self.endpoint, data=data)
        assert response.status_code == HTTP_403_FORBIDDEN, response.content
        u = User.objects.create(username="u")
        client.force_authenticate(u)
        response = client.post(self.endpoint, data=data)
        assert response.status_code == HTTP_403_FORBIDDEN, response.content
        add_user_permission(u, make_perm_add_department)
        response = client.post(self.endpoint, data=data)
        assert is_success(response.status_code), response.content

    def test_perm_change(self, db, client, make_perm_change_department):
        d = Department.objects.create(abbrev="dpt")
        data = {"name": "department"}
        response = client.put(f"{self.endpoint}{d.id}/", data=data)
        assert response.status_code == HTTP_403_FORBIDDEN, response.content
        response = client.patch(f"{self.endpoint}{d.id}/", data=data)
        assert response.status_code == HTTP_403_FORBIDDEN, response.content
        u = User.objects.create(username="u")
        client.force_authenticate(u)
        response = client.put(f"{self.endpoint}{d.id}/", data=data | {"abbrev": "d"})
        assert response.status_code == HTTP_403_FORBIDDEN, response.content
        response = client.patch(f"{self.endpoint}{d.id}/", data=data)
        assert response.status_code == HTTP_403_FORBIDDEN, response.content
        add_user_permission(u, make_perm_change_department)
        response = client.put(f"{self.endpoint}{d.id}/", data=data | {"abbrev": "d"})
        assert is_success(response.status_code), response.content
        response = client.patch(f"{self.endpoint}{d.id}/", data=data)
        assert is_success(response.status_code), response.content
