import django_filters.rest_framework as filters
from rest_framework import permissions, viewsets

import base.models as bm

from . import serializers


class CourseStartTimeFilter(filters.FilterSet):
    class Meta:
        model = bm.CourseStartTimeConstraint
        fields = ("department_id",)


class CourseStartTimeConstraintsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the courses start time constraints.

    """

    permission_classes = [permissions.AllowAny]
    queryset = bm.CourseStartTimeConstraint.objects.all()
    serializer_class = serializers.CourseStartTimeConstraintsSerializer
    filterset_class = CourseStartTimeFilter
