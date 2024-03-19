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

from django.urls import re_path

from solve_board import views

app_name="solve_board"

urlpatterns = [
    re_path(r'^fetch_context/(?P<train_prog>[a-zA-Z]\w{1,4})/(?P<period>)/$', views.fetch_context, name="fetch_context"),
    re_path(r'^main/$', views.main_board, name="main_board"),
    re_path(r'^analyse/(?P<train_prog>[a-zA-Z]\w{1,4})/(?P<period>)/(?P<type>[a-zA-Z]\w{1,30})$', views.launch_pre_analyse, name="pre_analyse")
#    re_path(r'^run/(?P<timestamp>[0-9-]+)?$', views.run, name="run"),
]
