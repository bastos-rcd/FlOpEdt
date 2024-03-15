import rest_framework.serializers as rf_s
from rest_framework import permissions, viewsets

from drf_spectacular.utils import extend_schema

from . import serializers
import base.models as bm


class EdtVersionQueryParamsSerializer(rf_s.Serializer):
    from_date = rf_s.DateField()
    to_date = rf_s.DateField()
    dept_id = rf_s.IntegerField(required=False)
    major_version = rf_s.IntegerField(required=False)


@extend_schema(parameters=[EdtVersionQueryParamsSerializer])
class EdtVersionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.EdtVersionFullSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return bm.EdtVersion.objects.none()

        qp_serializer = EdtVersionQueryParamsSerializer(data=self.request.query_params)
        qp_serializer.is_valid(raise_exception=True)
        qp_params = qp_serializer.validated_data

        params = dict()
        params["period__start_date__gte"] = qp_params.pop("from_date")
        params["period__end_date__lte"] = qp_params.pop("to_date")
        if "dept_id" in params:
            params["department__id"] = qp_params.pop("dept_id")
        if "major_version" in params:
            params["version__major"] = qp_params.pop["major_version"]

        return bm.EdtVersion.objects.filter(**params).select_related("period")
