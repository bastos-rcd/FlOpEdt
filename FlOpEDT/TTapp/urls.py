from django.urls import path

import TTapp.views

app_name = "TTapp"

urlpatterns = [
    path(
        "side_panel/<int:period_id>/",
        TTapp.views.available_major_versions,
        name="available_major_versions",
    ),
    path(
        "check_swap/<int:period_id>/<int:major>/",
        TTapp.views.check_swap,
        name="check_swap",
    ),
    path("swap/<int:period_id>/<int:major>/", TTapp.views.swap, name="swap"),
    path(
        "delete_version/<int:period_id>/<int:major>/",
        TTapp.views.delete_version,
        name="delete_version",
    ),
    path(
        "duplicate_version/<int:period_id>/<int:major>/",
        TTapp.views.duplicate_version,
        name="duplicate_version",
    ),
    path(
        "delete_all_unused_versions/<int:period_id>/",
        TTapp.views.delete_all_unused_versions,
        name="delete_all_unused_versions",
    ),
    path(
        "reassign_rooms/<int:period_id>/<int:major>/",
        TTapp.views.reassign_rooms,
        name="reassign_rooms",
    ),
    path(
        "duplicate_in_other_periods/<int:period_id>/<int:major>/",
        TTapp.views.duplicate_in_other_periods,
        name="duplicate_in_other_periods",
    ),
    path("fetch_group_lunch/", TTapp.views.fetch_group_lunch, name="fetch_group_lunch"),
]
