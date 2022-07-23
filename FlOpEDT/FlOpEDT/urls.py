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


"""FlOpEDT URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf import settings
from django.urls import path, re_path
from django.contrib import admin
from django.views.generic import RedirectView
from django.views.i18n import JavaScriptCatalog
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import gettext_lazy as _


from base import views


js_info_dict = {
    'packages': ('languages', )
}


urlpatterns = [

    # favicon
    # ----------------------------
    url(views.fav_regexp,
        views.favicon,
        name="favicon"),
    re_path(r'^$', views.index, name='index')
]

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r'^rosetta/', include('rosetta.urls'))
    ]


urlpatterns += i18n_patterns(
    re_path(r'^jsi18n/$', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    re_path(r'^admin$', RedirectView.as_view(url='/admin/')),
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^accounts/', include('people.urls')),
    re_path(r'^citations/', include('quote.urls')),
    re_path(r'^edt/(?P<department>[a-zA-Z]\w{0,6})/', include('base.urls')),
    re_path(r'^solve-board/(?P<department>[a-zA-Z]\w{0,6})/', include('solve_board.urls')),
    re_path(r'^ics/(?P<department>[a-zA-Z]\w{0,6})/', include('ics.urls')),
    re_path(r'^configuration/', include('configuration.urls')),
    re_path(r'^ttapp/(?P<department>[a-zA-Z]\w{0,6})/', include('TTapp.urls')),
    re_path(r'^game/', include('easter_egg.urls')),
    re_path(r'^flopeditor/', include('flopeditor.urls')),
    re_path(r'^display/(?P<department>[a-zA-Z]\w{0,6})/', include('displayweb.urls')),
    re_path(r'^cstmanager/', include('cstmanager.urls')),
    path('api/', include('api.urls')),

)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
