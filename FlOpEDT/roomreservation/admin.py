from django.contrib import admin
from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget

from base.admin import MyModelAdmin
from roomreservation.models import RoomReservationType


class RoomReservationTypeAdmin(MyModelAdmin):
    list_display = ("name", "bg_color")
    ordering = ("name",)


admin.site.register(RoomReservationType, RoomReservationTypeAdmin)
