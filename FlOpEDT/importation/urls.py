from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path

from . import views

app_name = "importation"

urlpatterns = [
    url(r"^$", views.importation_dispo, name="importation_dispo"),
    url(
        r"^get_dispo_file/(?P<period>[a-zA-Z0-9]+)/$",
        views.get_dispo_file,
        name="get_dispo_file",
    ),
]
