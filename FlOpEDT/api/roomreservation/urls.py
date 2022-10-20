from rest_framework import routers
from api.roomreservation import views

routerRoomReservation = routers.SimpleRouter()

routerRoomReservation.register(r'reservation', views.RoomReservationViewSet, basename='reservation')
routerRoomReservation.register(r'reservationtype', views.RoomReservationTypeViewSet, basename='reservationtype')
routerRoomReservation.register(r'reservationperiodicity', views.ReservationPeriodicityViewSet, basename='reservationperiodicity')
routerRoomReservation.register(r'reservationperiodicitybyweek', views.ReservationPeriodicityByWeekViewSet, basename='reservationperiodicitybyweek')
routerRoomReservation.register(r'reservationperiodicityeachmonthsamedate', views.ReservationPeriodicityEachMonthSameDateViewSet, basename='reservationperiodicityeachmonthsamedate')
routerRoomReservation.register(r'reservationperiodicitybymonthxchoice', views.ReservationPeriodicityByMonthXChoiceViewSet, basename='reservationperiodicitybymonthxchoice')
routerRoomReservation.register(r'reservationperiodicitybymonth', views.ReservationPeriodicityByMonthViewSet, basename='reservationperiodicitybymonth')
routerRoomReservation.register(r'reservationperiodicitytype', views.ReservationPeriodicityTypeViewSet, basename='reservationperiodicitytype')
