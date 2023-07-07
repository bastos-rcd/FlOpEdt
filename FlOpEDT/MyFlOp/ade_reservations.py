# coding: utf-8
# -*- coding: utf-8 -*-

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

import csv
import datetime
from base.models import Room
from roomreservation.models import RoomReservation, RoomReservationType
from django.db import transaction
from people.models import User
from ics import Calendar
import requests

ade_reservations_filename = f"/var/flopedt/tmp/misc/Export_Salles_utf8.csv"
ade_reservations_ics_url = "https://sedna.univ-fcomte.fr/jsp/custom/ufc/cal.jsp?data=7d2be45f7963012e7330cb059c72f77f1c3c057a13954fcb73e210929d5c5728c6412a77b23057dfc03c0942972f2bb1de5b64a61bcf70e2db430bbabcd5338c57066d130b9a7621faf9c42a9c2ef5fc74ed3b5838e481265e30c5a102f3790c16e4212ea9e129e77f2e06fc8dfba77830a5f72847b0c2c00c79892a4ff650a79975b678970c7724d3997a83ca8b8c5b1e3e63b85b4fe4163e5444e84e51c091,1"



@transaction.atomic
def import_ade_reservations_from_tomorrow(ade_reservations_filename=None):
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    if ade_reservations_filename is None:
        ade_reservations_filename = f"/var/flopedt/tmp/misc/Export_Salles_utf8.csv"
    import_reservations_from_ade_csv_file(csv_filename=ade_reservations_filename, from_date=tomorrow)


@transaction.atomic
def import_reservations_from_ade_ics_url(ade_reservations_ics_url=ade_reservations_ics_url, 
                                         future_only=True):
    responsible = User.objects.get_or_create(username='ADE')[0]
    reservation_type = RoomReservationType.objects.get_or_create(name='ADE')[0]
    room_reservations_to_delete = RoomReservation.objects.filter(reservation_type=reservation_type, 
                                                                 responsible=responsible)
    if future_only:
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        room_reservations_to_delete = room_reservations_to_delete.filter(date__gte=tomorrow)
    
    room_reservations_to_delete.delete()
    calendar = Calendar(requests.get(ade_reservations_ics_url).text)
    for e in calendar.events:
        date = e.begin.date()
        if future_only:
            if date < tomorrow:
                continue
        concateneted_room_names = e.location
        room_names = concateneted_room_names.split(',')
        rooms = set()
        for room_name in room_names:
            room = Room.objects.get_or_create(name=room_name)[0]
            rooms.add(room)
        start_time = e.begin.time()
        end_time = e.end.time()
        description = e.description.split('(')[0]
        title = "ADE"
        for room in rooms:
            RoomReservation.objects.create(room=room, 
                                           reservation_type=reservation_type, 
                                           date=date, 
                                           start_time=start_time, 
                                           end_time=end_time,
                                           title=title,
                                           responsible=responsible,
                                           description=description) 


@transaction.atomic
def import_reservations_from_ade_csv_file(csv_filename,
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
    with open(csv_filename, newline='') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';', quotechar='|')
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