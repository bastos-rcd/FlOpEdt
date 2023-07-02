import csv
import datetime
from base.models import Room
from roomreservation.models import RoomReservation, RoomReservationType
from django.db import transaction
from people.models import User


@transaction.atomic
def import_ade_reservations_from_tomorrow():
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    ade_reservations_filename = f"/var/flopedt/tmp/misc/Export_Salles_utf8.csv"
    import_reservations_from_ade(filename=ade_reservations_filename, from_date=tomorrow)


@transaction.atomic
def import_reservations_from_ade(filename,
                                 from_date=None,
                                 to_date=None):
    responsible = User.objects.get_or_create(username='ADE')[0]
    reservation_type = RoomReservationType.objects.get_or_create(name='ADE')[0]
    room_reservations_to_delete = RoomReservation.objects.filter(reservation_type=reservation_type, 
                                                                 responsible=responsible)
    if from_date is not None:
        room_reservations_to_delete = room_reservations_to_delete.filter(date__gte=from_date)
    if to_date is not None:
        room_reservations_to_delete = room_reservations_to_delete.filter(date__lte=to_date)
    room_reservations_to_delete.delete()
    with open(filename, newline='') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=';', quotechar='|')
        next(csv_reader)
        for row in csv_reader:
            if not row:
                continue
            date_str = row[1]
            date = datetime.datetime.strptime(date_str, '%d/%m/%Y').date()
            if from_date is not None:
                if date < from_date:
                    continue
            if to_date is not None:
                if date > to_date:
                    continue
            room_name = row[0]
            room = Room.objects.get_or_create(name=room_name)[0]
            start_time_str = row[2]
            start_time = datetime.datetime.strptime(start_time_str, '%Hh%M').time()
            end_time_str = row[3]
            end_time = datetime.datetime.strptime(end_time_str, '%Hh%M').time()
            title = row[4]
            RoomReservation.objects.create(room=room, 
                                           reservation_type=reservation_type, 
                                           date=date, 
                                           start_time=start_time, 
                                           end_time=end_time,
                                           title=title,
                                           responsible=responsible) 