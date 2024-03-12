from rest_framework import viewsets, permissions
import django_filters.rest_framework as filters
from . import serializers


import base.models as bm


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
