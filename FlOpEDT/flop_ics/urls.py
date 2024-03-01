from django.urls import path
from flop_ics.feeds import TutorEventFeed, RoomEventFeed, StructuralGroupEventFeed, TransversalGroupEventFeed, RegenFeed

from flop_ics import views

app_name = 'flop_ics'

urlpatterns = [
    path(r'', views.index, name="index"),
    path(r'tutor/<int:tutor_id>.ics', TutorEventFeed(), name="tutor"),
    path(r'room/<int:room_id>.ics', RoomEventFeed(), name="room"),
    path(r'structural_group/<int:group_id>.ics', StructuralGroupEventFeed(), name="structural_group"),
    path(r'transversal_group/<int:group_id>.ics', TransversalGroupEventFeed(), name="transversal_group"),
    path(r'regen/<int:dep_id>.ics', RegenFeed(), name="regen"),
]
