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
