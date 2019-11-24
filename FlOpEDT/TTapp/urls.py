from django.conf.urls import url, include
from django.urls import path

import TTapp.views

app_name="TTapp"

urlpatterns = [
    path('side_panel/<str:dept>/<int:year>/<int:week>', TTapp.views.available_work_copies, name="available_work_copies"),
    path('swap/<str:dept>/<int:year>/<int:week>/<int:work_copy>', TTapp.views.swap, name="swap"),
    path('reassign_rooms/<str:dept>/<int:year>/<int:week>/<int:work_copy>', TTapp.views.reassign_rooms, name="reassign_rooms"),
]