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

from rest_framework import serializers

import displayweb.models as dwm
import quote.models as q

# ----------
# -- QUOTE -
# ----------


class QuoteTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = q.QuoteType
        fields = "__all__"


class QuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = q.Quote
        fields = "__all__"


# ---------------
# -- DISPLAYWEB -
# ---------------


class BreakingNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = dwm.BreakingNews
        fields = "__all__"


class ModuleDisplaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = dwm.ModuleDisplay
        fields = "__all__"


class TrainingProgrammeDisplaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = dwm.TrainingProgrammeDisplay
        fields = "__all__"


class GroupDisplaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = dwm.GroupDisplay
        fields = "__all__"


#
#   Log-in-and-out
#
