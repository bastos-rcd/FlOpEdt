from django.conf.urls import url
from . import views

app_name="configuration"

urlpatterns = [
    url(r'^$', views.configuration, name="configuration"),
    url(r'^upload_config/$', views.import_config_file, name="ul_config"),
    url(r'^upload_planif/$', views.import_planif_file, name="ul_planif"),
    url(r'^download_config/$', views.get_config_file, name="dl_config"),
    url(r'^download_planif/$', views.get_planif_file, name="dl_planif"),
    url(r'^mk_and_dl_blank_planif/$', views.mk_and_dl_planif, {'with_courses': False}, name="mk_and_dl_blank_planif"),
    url(r'^mk_and_dl_fullfilled_planif/$', views.mk_and_dl_planif, {'with_courses': True}, name="mk_and_dl_fullfilled_planif"),
]
