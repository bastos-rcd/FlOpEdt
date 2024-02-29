import json
from rest_framework import status


def retrieve_elements(response, n=None):
    assert status.is_success(response.status_code), (
        f"Unsuccessful request (status {response.status_code})",
        response,
    )
    response_dict = json.loads(response.content)
    if n is not None:
        assert len(response_dict) == n, (
            f"Wrong number of elements: expected {n} got {len(response_dict)}",
            response_dict,
        )
    return response_dict


def add_user_permission(user, permission):
    user.user_permissions.add(permission)
    if hasattr(user, "_perm_cache"):
        del user._perm_cache
    if hasattr(user, "_user_perm_cache"):
        del user._user_perm_cache
    assert (
        f"{permission.content_type.app_label}.{permission.codename}"
        in user.get_all_permissions()
    ), user.get_all_permissions()
