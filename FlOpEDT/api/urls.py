# This file is part of the FlOpEDT/FlOpScheduler project.
# Copyright (c) 2017
# Authors: Iulian Ober, Paul Renaud-Goud, Pablo Seban, et al.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public
# License along with this program. If not, see
# <http://www.gnu.org/licenses/>.
# 
# You can be released from the requirements of the license by purchasing
# a commercial license. Buying such a license is mandatory as soon as
# you develop activities involving the FlOpEDT/FlOpScheduler software
# without disclosing the source code of your own applications.

from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from django.urls import path
from django.views.generic import TemplateView
from drf_yasg import openapi
# from rest_framework_swagger.renderers import SwaggerUIRenderer, OpenAPIRenderer
from drf_yasg.views import get_schema_view
from rest_framework import routers, permissions
from rest_framework.authtoken.views import obtain_auth_token

import api.base.views as views_base
import api.fetch.views as views_fetch
from api import views
from api.TTapp.urls import routerTTapp
from api.base.courses.urls import routerCourses
from api.base.groups.urls import routerGroups
from api.base.rooms.urls import routerRooms
from api.base.urls import routerBase
from api.fetch.urls import routerFetch
from api.myflop.urls import routerMyFlop
from api.people.urls import routerPeople
from api.preferences.urls import routerPreferences
from api.roomreservation.urls import routerRoomReservation

#####################################
# URLS based on django applications #
#####################################

app_name = "api"

routerDisplayweb = routers.SimpleRouter()

routerDisplayweb.register(r'breakingnews', views.BreakingNewsViewSet)
routerDisplayweb.register(r'moduledisplays', views.ModuleDisplaysViewSet)
routerDisplayweb.register(r'trainingprogrammedisplays', views.TrainingProgrammeDisplaysViewSet)
routerDisplayweb.register(r'groupdisplays', views.GroupDisplaysViewSet)

######################
# User friendly URLS #
######################

routerExtra = routers.SimpleRouter()

routerExtra.register('bknews', views_fetch.BKNewsViewSet, basename="bknews")
routerExtra.register('quote/random', views.RandomQuoteViewSet, basename="random-quote")
routerExtra.register('quote', views.QuoteViewSet)
routerExtra.register('week-infos', views.WeekInfoViewSet, basename="week-infos")

################
# SWAGGER VIEW #
################
schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    url(r'^$', views_base.LoginView.as_view(), name='api_root'),
    url(r'^logout/$', views_base.LogoutView.as_view()),
    url(r'^backoffice/$', login_required(TemplateView.as_view(template_name='logout.html'))),
    path('base/', include((routerBase.urls, 'api'), namespace='base')),
    path('user/', include((routerPeople.urls, 'api'), namespace="people")),
    path('display/', include(routerDisplayweb.urls)),
    path('ttapp/', include((routerTTapp.urls, 'api'), namespace='ttapp')),
    path('fetch/',
         include((routerFetch.urls, 'api'), namespace='fetch')),
    path('rest-auth/', include('rest_auth.urls')),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    url('doc/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('preferences/', include(routerPreferences.urls)),
    path('rooms/',
         include((routerRooms.urls, 'api'), namespace='rooms')),
    path('courses/',
         include((routerCourses.urls, 'api'), namespace='course')),
    path('groups/',
         include((routerGroups.urls, 'api'), namespace='groups')),
    path('extra/',
         include((routerExtra.urls, 'api'), namespace='extra')),
    path('myflop/',
         include((routerMyFlop.urls, 'api'), namespace='myflop')),
    path('roomreservations/',
         include((routerRoomReservation.urls, 'api'), namespace='roomreservations')),
]
