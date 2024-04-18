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

import datetime as dt

from django.db.models.signals import post_save
from django.dispatch import receiver

from base.models import UserAvailability
from people.models import Tutor


@receiver(post_save)
def create_tutor_default_availability(sender, instance, created, **kwargs):
    # pylint: disable=unused-argument
    if isinstance(instance, Tutor) and created:
        # disable if instance comes from loaddata
        if kwargs.get("raw") is True:
            return
        for d in range(1, 8):
            UserAvailability.objects.create(
                user=instance,
                start_time=dt.datetime(1, 1, d, 0),
                duration=dt.timedelta(hours=24),
            )
