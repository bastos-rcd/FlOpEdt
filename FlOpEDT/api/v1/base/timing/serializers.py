from rest_framework import serializers

import base.models as bm


class SchedulingPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.SchedulingPeriod
        fields = ("id", "name", "start_date", "end_date", "mode", "department_id")
