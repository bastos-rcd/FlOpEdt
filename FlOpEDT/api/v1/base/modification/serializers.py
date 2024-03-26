from rest_framework import serializers

import base.models as bm
from api.v1.base.timing.serializers import SchedulingPeriodSerializer


class TimetableVersionShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.TimetableVersion
        fields = ("id", "minor", "major")


class TimetableVersionFullSerializer(serializers.ModelSerializer):
    period = SchedulingPeriodSerializer()

    class Meta:
        model = bm.TimetableVersion
        fields = ("id", "department_id", "period", "major", "minor")
