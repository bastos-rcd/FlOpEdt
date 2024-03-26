from django.urls import path

from . import views

app_name = "configuration"

urlpatterns = [
    path("", views.configuration, name="configuration"),
    path("upload_config", views.import_config_file, name="ul_config"),
    path("upload_planif", views.import_planif_file, name="ul_planif"),
    path("download_config", views.get_config_file, name="dl_config"),
    path("download_planif", views.get_planif_file, name="dl_planif"),
    path(
        "mk_and_dl_blank_planif",
        views.mk_and_dl_planif,
        {"with_courses": False},
        name="mk_and_dl_blank_planif",
    ),
    path(
        "mk_and_dl_fullfilled_planif",
        views.mk_and_dl_planif,
        {"with_courses": True},
        name="mk_and_dl_fullfilled_planif",
    ),
    path(
        "mk_and_dl_fullfilled_database_file",
        views.mk_and_dl_database_file,
        name="mk_and_dl_fullfilled_database_file",
    ),
]
