from django.conf.urls import url, include
from django.urls import path

import TTapp.views

app_name = "TTapp"

urlpatterns = [
    path('side_panel/<int:year>/<int:week>',
         TTapp.views.available_work_copies,
         name="available_work_copies"),
    path('check_swap/<int:year>/<int:week>/<int:work_copy>',
         TTapp.views.check_swap,
         name="check_swap"),
    path('swap/<int:year>/<int:week>/<int:work_copy>',
         TTapp.views.swap,
         name="swap"),
    path('delete_work_copy/<int:year>/<int:week>/<int:work_copy>',
         TTapp.views.delete_work_copy,
         name="delete_work_copy"),
    path('duplicate_work_copy/<int:year>/<int:week>/<int:work_copy>',
         TTapp.views.duplicate_work_copy,
         name="duplicate_work_copy"),
    path('delete_all_unused_work_copies/<int:year>/<int:week>',
         TTapp.views.delete_all_unused_work_copies,
         name="delete_all_unused_work_copies"),
    path('reassign_rooms/<int:year>/<int:week>/<int:work_copy>',
         TTapp.views.reassign_rooms,
         name="reassign_rooms"),
    path('duplicate_in_other_weeks/<int:year>/<int:week>/<int:work_copy>',
         TTapp.views.duplicate_in_other_weeks,
         name="duplicate_in_other_weeks"),
    path('fetch_group_lunch',
         TTapp.views.fetch_group_lunch,
         name="fetch_group_lunch"),
]
