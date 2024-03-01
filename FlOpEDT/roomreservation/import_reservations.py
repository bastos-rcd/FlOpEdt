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
from pytz import timezone
import configparser, os
import logging

logger = logging.getLogger("base")
# Let's parse the configuration file
flop_config = configparser.ConfigParser()
flop_config.read(os.environ.get("FLOP_CONFIG_FILE"))
ics_url = flop_config['roomreservations-import']['ics_url']
key_exclusion = flop_config['roomreservations-import']['key_exclusion']
exclude_if_key_contains = flop_config['roomreservations-import']['exclude_if_key_contains']
imported_reservations_name=flop_config['roomreservations-import']['imported_reservations_name']

paris = timezone("Europe/Paris")

@transaction.atomic
def import_reservations_from_ics_url(room_reservations_ics_url=ics_url, 
                                     future_only=True,
                                     key_exclusion=key_exclusion,
                                     exclude_if_key_contains=exclude_if_key_contains,
                                     default_responsible_name=imported_reservations_name):
    try:
        calendar = Calendar(requests.get(room_reservations_ics_url).text)
    except:
        logger.warning("Error while trying to get the ics file from URL: " + room_reservations_ics_url)
        return
    
    responsible = User.objects.get_or_create(username=default_responsible_name)[0]
    reservation_type = RoomReservationType.objects.get_or_create(name=default_responsible_name)[0]
    room_reservations_to_delete = RoomReservation.objects.filter(reservation_type=reservation_type, 
                                                                 responsible=responsible)
    if future_only:
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        room_reservations_to_delete = room_reservations_to_delete.filter(date__gte=tomorrow)
    
    room_reservations_to_delete.delete()
    for e in calendar.events:
        begin = e.begin.astimezone(paris)
        end = e.end.astimezone(paris)
        to_be_saved=True
        date = begin.date()
        if future_only:
            if date < tomorrow:
                continue
        concateneted_room_names = e.location
        room_names = concateneted_room_names.split(',')
        rooms = set()
        for room_name in room_names:
            room = Room.objects.get_or_create(name=room_name)[0]
            rooms.add(room)
        start_time = begin.time()
        end_time = end.time()
        description = e.description
        title = e.name[:30]
        if exclude_if_key_contains in getattr(e, key_exclusion):
            to_be_saved=False
            continue
        if to_be_saved:
            for room in rooms:
                RoomReservation.objects.create(room=room, 
                                               reservation_type=reservation_type, 
                                               date=date, 
                                               start_time=start_time, 
                                               end_time=end_time,
                                               title=title,
                                               responsible=responsible,
                                               description=description)