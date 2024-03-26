import copy
import datetime as dt

import pytest
from django.utils.duration import duration_string
from rest_framework.status import HTTP_403_FORBIDDEN, is_success

from api.v1.tests.utils import add_user_permission, retrieve_elements
from base.models.availability import UserAvailability
from base.models.groups import Department
from base.models.rooms import Room
from people.models import FullStaff, Tutor, User


class TestListUserAvailability:
    endpoint = f"/fr/api/v1/availability/user/"
    target_dates = {
        "from_date": "0001-01-02",
        "to_date": "0001-01-04",
    }

    def test_user_or_dept_required(self, client):
        with pytest.raises(AssertionError) as e_info:
            retrieve_elements(client.get(self.endpoint, self.target_dates))

    def test_list_date(self, client, make_default_week_user: None):
        user = User.objects.first()
        user.is_superuser = True
        user.save()
        client.force_authenticate(user)
        wanted = self.target_dates | {"user_id": user.id}
        response = retrieve_elements(client.get(self.endpoint, wanted), 2)
        response = sorted(response, key=lambda ua: ua["start_time"])
        assert len(response) == 2
        response = [
            {k: v for k, v in r.items() if k in ["start_time", "duration"]}
            for r in response
        ]
        assert response == [
            {
                "start_time": dt.datetime(1, 1, 2, 0).isoformat(),
                "duration": duration_string(dt.timedelta(hours=24)),
            },
            {
                "start_time": dt.datetime(1, 1, 3, 0).isoformat(),
                "duration": duration_string(dt.timedelta(hours=24)),
            },
        ], response.content

    def test_perm_view_mine_denied(self, client, make_users):
        make_users(1)
        user = User.objects.first()
        client.force_authenticate(user)
        wanted = self.target_dates | {"user_id": user.id}
        response = client.get(self.endpoint, wanted)
        assert response.status_code == HTTP_403_FORBIDDEN, response

    def test_perm_view_mine_allowed(
        self, client, make_users, make_perm_view_my_user_av
    ):
        make_users(1)
        user = User.objects.first()
        add_user_permission(user, make_perm_view_my_user_av)
        client.force_authenticate(user)
        wanted = self.target_dates | {"user_id": user.id}
        response = client.get(self.endpoint, wanted)
        assert is_success(response.status_code), response

    def test_perm_view_other_user_allowed(
        self, client, make_users, make_perm_view_any_user_av
    ):
        make_users(2)
        user = User.objects.first()
        add_user_permission(user, make_perm_view_any_user_av)
        other = User.objects.all().exclude(id=user.id)[0]
        client.force_authenticate(user)
        wanted = self.target_dates | {"user_id": other.id}
        response = client.get(self.endpoint, wanted)
        assert is_success(response.status_code), response

    def test_perm_view_other_user_allowed(self, client, make_users):
        make_users(2)
        user = User.objects.first()
        other = User.objects.all().exclude(id=user.id)[0]
        client.force_authenticate(user)
        wanted = self.target_dates | {"user_id": other.id}
        response = client.get(self.endpoint, wanted)
        assert response.status_code == HTTP_403_FORBIDDEN, response

    def test_perm_view_dept_allowed(
        self, client, make_users, make_perm_view_any_user_av
    ):
        make_users(1)
        user = User.objects.first()
        add_user_permission(user, make_perm_view_any_user_av)
        d = Department.objects.create(abbrev="d")
        client.force_authenticate(user)
        wanted = self.target_dates | {"dept_id": d.id}
        response = client.get(self.endpoint, wanted)
        assert is_success(response.status_code), response

    def test_perm_view_dept_allowed(self, client, make_users):
        make_users(1)
        user = User.objects.first()
        d = Department.objects.create(abbrev="d")
        client.force_authenticate(user)
        wanted = self.target_dates | {"dept_id": d.id}
        response = client.get(self.endpoint, wanted)
        assert response.status_code == HTTP_403_FORBIDDEN, response

    @pytest.mark.skip("Test subfactory")
    def test_facto(self, client, make_users_and_av):
        make_users_and_av(10)
        print(UserAvailability.objects.filter(user=User.objects.first()))
        assert User.objects.count() == 10, User.objects.all()
        assert (
            UserAvailability.objects.count() == 10 * 7
        ), UserAvailability.objects.all()


class TestUpdateUserAvailability:
    endpoint = f"/fr/api/v1/availability/update_user/"
    from_date = "1871-03-20"
    to_date = "1871-03-20"
    wanted = {
        "from_date": from_date,
        "to_date": to_date,
        "intervals": [
            {
                "start_time": f"{from_date}T00:00:00",
                "duration": "12:00:00",
                "value": 3,
            },
            {
                "start_time": f"{to_date}T12:00:00",
                "duration": "12:00:00",
                "value": 2,
            },
        ],
    }

    def test_update_single_day(self, client, make_user_hourly_commune):
        user = User.objects.first()
        user.is_superuser = True
        user.save()
        client.force_authenticate(user=user)
        push = self.wanted | {"subject_id": user.id}
        response = retrieve_elements(client.post(self.endpoint, push), 4)
        assert response == push

    def test_update_two_days(self, client, make_user_hourly_commune):
        user = User.objects.first()
        client.force_authenticate(user=user)
        push = copy.deepcopy(self.wanted) | {"subject_id": user.id}
        push["to_date"] = "1871-03-21"
        push["intervals"] += [
            {
                "start_time": f"{push['to_date']}T00:00:00",
                "duration": "10:00:00",
                "value": 4,
            },
            {
                "start_time": f"{push['to_date']}T10:00:00",
                "duration": "14:00:00",
                "value": 5,
            },
        ]
        response = retrieve_elements(client.post(self.endpoint, push), 4)
        assert response == push

    def test_update_cut_day_end(self, client, make_user_hourly_commune):
        user = User.objects.first()
        client.force_authenticate(user=user)
        push = copy.deepcopy(self.wanted) | {"subject_id": user.id}
        push["to_date"] = "1871-03-21"
        push["intervals"] += [
            {
                "start_time": f"{push['to_date']}T00:00:00",
                "duration": "10:00:00",
                "value": 4,
            },
        ]
        response = client.post(self.endpoint, push)
        assert not is_success(response.status_code), response

    def test_update_cut_day_middle(self, client, make_user_hourly_commune):
        user = User.objects.first()
        client.force_authenticate(user=user)
        push = copy.deepcopy(self.wanted) | {"subject_id": user.id}
        push["to_date"] = "1871-03-21"
        push["intervals"] += [
            {
                "start_time": f"{push['to_date']}T00:00:00",
                "duration": "10:00:00",
                "value": 4,
            },
            {
                "start_time": f"{push['to_date']}T12:00:00",
                "duration": "12:00:00",
                "value": 4,
            },
        ]
        response = client.post(self.endpoint, push)
        assert not is_success(response.status_code), response

    def test_perm_push_mine_denied(self, client, make_users):
        make_users(1)
        user = User.objects.first()
        client.force_authenticate(user=user)
        push = self.wanted | {"subject_id": user.id}
        response = client.post(self.endpoint, push)
        assert response.status_code == HTTP_403_FORBIDDEN, response.content

    def test_perm_push_mine_allowed(self, client, make_user_perm_push_my_user_av):
        user = make_user_perm_push_my_user_av
        client.force_authenticate(user=user)
        push = self.wanted | {"subject_id": user.id}
        assert user.id == push["subject_id"]
        response = client.post(self.endpoint, push)
        assert is_success(response.status_code), response.content

    def test_perm_push_other_denied(
        self, client, make_user_perm_push_my_user_av, make_users
    ):
        make_users(2)
        user = make_user_perm_push_my_user_av
        other = User.objects.all().exclude(id=user.id).first()
        client.force_authenticate(user=user)
        push = self.wanted | {"subject_id": other.id}
        response = client.post(self.endpoint, push)
        assert response.status_code == HTTP_403_FORBIDDEN, response.content

    def test_perm_push_other_allowed(
        self, client, make_user_perm_push_any_user_av, make_users
    ):
        make_users(2)
        user = make_user_perm_push_any_user_av
        other = User.objects.all().exclude(id=user.id).first()
        client.force_authenticate(user=user)
        push = self.wanted | {"subject_id": other.id}
        response = client.post(self.endpoint, push)
        assert is_success(response.status_code), response.content


class TestUpdateRoomAvailability:
    endpoint = f"/fr/api/v1/availability/update_room/"
    from_date = "1848-04-17"
    to_date = "1848-04-18"
    wanted = {
        "from_date": from_date,
        "to_date": to_date,
        "intervals": [
            {
                "start_time": f"{from_date}T00:00:00",
                "duration": "10:00:00",
                "value": 2,
            },
            {
                "start_time": f"{from_date}T10:00:00",
                "duration": "10:00:00",
                "value": 2,
            },
            {
                "start_time": f"{from_date}T20:00:00",
                "duration": "04:00:00",
                "value": 2,
            },
            {
                "start_time": f"{to_date}T00:00:00",
                "duration": "04:00:00",
                "value": 2,
            },
            {
                "start_time": f"{to_date}T04:00:00",
                "duration": "20:00:00",
                "value": 2,
            },
        ],
    }

    def test_update(self, client, make_rooms_and_av):
        room = make_rooms_and_av(3)[0]
        user = User.objects.create_superuser(username="u")
        client.force_authenticate(user=user)
        push = self.wanted | {"subject_id": room.id}
        response = retrieve_elements(client.post(self.endpoint, push), 4)
        assert response == push

    def test_perm_push_denied(self, client, db, make_users):
        make_users(1)
        r = Room.objects.create(name="r")
        u = User.objects.first()
        data = self.wanted | {"subject_id": r.id}

        client.force_authenticate(u)
        response = client.post(self.endpoint, data=data)
        assert response.status_code == HTTP_403_FORBIDDEN, response.content

    def test_perm_push_allowed(self, client, make_user_perm_push_room_av):
        r = Room.objects.create(name="r")
        u = make_user_perm_push_room_av
        data = self.wanted | {"subject_id": r.id}

        client.force_authenticate(u)
        response = client.post(self.endpoint, data=data)
        assert is_success(response.status_code), response.content


class TestListUserAvailabilityDefault:
    endpoint = f"/fr/api/v1/availability/user-default-week/"

    def test_tutor_creation(self, client, make_default_week_user):
        user = User.objects.first()
        tutor = Tutor.objects.create(username="tutor")
        user_av = UserAvailability.objects.filter(user=user).order_by("start_time")
        tutor_av = UserAvailability.objects.filter(user=tutor).order_by("start_time")
        assert len(user_av) == len(tutor_av)
        for ua, ta in zip(user_av, tutor_av):
            assert (
                ua.start_time == ta.start_time
                and ua.duration == ta.duration
                and ua.value == ta.value
            )

    def test_tutor_subclass_creation(self, client, make_default_week_user):
        user = User.objects.first()
        tutor = FullStaff.objects.create(username="fs")
        user_av = UserAvailability.objects.filter(user=user).order_by("start_time")
        tutor_av = UserAvailability.objects.filter(user=tutor).order_by("start_time")
        assert len(user_av) == len(tutor_av)
        for ua, ta in zip(user_av, tutor_av):
            assert (
                ua.start_time == ta.start_time
                and ua.duration == ta.duration
                and ua.value == ta.value
            )

    def test_list(self, client, make_default_week_user, make_users):
        user = User.objects.first()
        user.is_superuser = True
        user.save()
        make_users(2)
        expected = []
        for day in range(1, 8):
            expected.append(
                {
                    "subject_type": "user",
                    "subject_id": user.id,
                    "start_time": f"0001-01-{day:02d}T00:00:00",
                    "duration": duration_string(dt.timedelta(hours=24)),
                    "value": 8,
                }
            )
        client.force_authenticate(user)
        response = retrieve_elements(client.get(self.endpoint, {"user_id": user.id}), 7)
        assert sorted(expected, key=lambda a: a["start_time"]) == sorted(
            response, key=lambda a: a["start_time"]
        )

    def test_perm_mine_denied(self, client, make_default_week_user):
        user = User.objects.first()
        client.force_authenticate(user)
        response = client.get(self.endpoint, {"user_id": user.id})
        assert response.status_code == HTTP_403_FORBIDDEN, response


class TestUpdateUserAvailabilityDefault:
    endpoint = f"/fr/api/v1/availability/update_user-default-week/"
    from_date = "1929-10-29"
    to_date = "1929-10-29"
    wanted = {
        "from_date": from_date,
        "to_date": to_date,
        "intervals": [
            {
                "start_time": f"{from_date}T00:00:00",
                "duration": "12:00:00",
                "value": 3,
            },
            {
                "start_time": f"{to_date}T12:00:00",
                "duration": "12:00:00",
                "value": 2,
            },
        ],
    }

    def test_update(self, db, client, make_default_week_user):
        user = User.objects.first()
        user.is_superuser = True
        user.save()

        client.force_authenticate(user)
        response = client.post(
            self.endpoint,
            self.wanted
            | {
                "subject_id": user.id,
                "subject_type": "user",
            },
        )
        assert is_success(response.status_code), response
        response = retrieve_elements(
            client.get(
                "/fr/api/v1/availability/user-default-week/", {"user_id": user.id}
            ),
            8,
        )
        expected = copy.deepcopy(self.wanted["intervals"])
        expected[0]["start_time"] = "0001-01-02T00:00:00"
        expected[1]["start_time"] = "0001-01-02T12:00:00"
        response.sort(key=lambda a: a["start_time"])
        assert [
            {
                k: v
                for (k, v) in inter.items()
                if k in ["start_time", "duration", "value"]
            }
            for inter in response[1:3]
        ] == expected, response

    def test_perm_push_mine_denied(self, client, make_users):
        make_users(1)
        user = User.objects.first()
        client.force_authenticate(user=user)
        push = self.wanted | {"subject_id": user.id}
        response = client.post(self.endpoint, push)
        assert response.status_code == HTTP_403_FORBIDDEN, response.content

    def test_perm_push_mine_allowed(self, client, make_user_perm_push_my_user_av):
        user = make_user_perm_push_my_user_av
        client.force_authenticate(user=user)
        push = self.wanted | {"subject_id": user.id}
        assert user.id == push["subject_id"]
        response = client.post(self.endpoint, push)
        assert is_success(response.status_code), response.content

    def test_perm_push_other_denied(
        self, client, make_user_perm_push_my_user_av, make_users
    ):
        make_users(2)
        user = make_user_perm_push_my_user_av
        other = User.objects.all().exclude(id=user.id).first()
        client.force_authenticate(user=user)
        push = self.wanted | {"subject_id": other.id}
        response = client.post(self.endpoint, push)
        assert response.status_code == HTTP_403_FORBIDDEN, response.content

    def test_perm_push_other_allowed(
        self, client, make_user_perm_push_any_user_av, make_users
    ):
        make_users(2)
        user = make_user_perm_push_any_user_av
        other = User.objects.all().exclude(id=user.id).first()
        client.force_authenticate(user=user)
        push = self.wanted | {"subject_id": other.id}
        response = client.post(self.endpoint, push)
        assert is_success(response.status_code), response.content


class TestRoomAvailabilityActual:
    endpoint = f"/fr/api/v1/availability/room/"
