from rest_framework import serializers

import base.models as bm


class CourseStartTimeConstraintsSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.CourseStartTimeConstraint
        fields = (
            "department_id",
            "duration",
            "allowed_start_times",
        )
