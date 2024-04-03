from django.contrib import admin
from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget

from base.admin import DepartmentModelAdmin
from base.models import Module
from displayweb.models import BreakingNews, ModuleDisplay, TutorDisplay
from people.models import Tutor


class BreakingNewsResource(resources.ModelResource):
    class Meta:
        model = BreakingNews
        fields = (
            "id",
            "x_beg",
            "x_end",
            "y",
            "txt",
            "fill_color",
            "strk_color",
            "is_linked",
        )


class BreakingNewsAdmin(DepartmentModelAdmin):
    list_display = (
        "week",
        "year",
        "x_beg",
        "x_end",
        "y",
        "txt",
        "fill_color",
        "strk_color",
    )
    ordering = ("-year", "-week")


class TutorDisplayResource(resources.ModelResource):
    tutor = fields.Field(
        column_name="key", attribute="tutor", widget=ForeignKeyWidget(Tutor, "username")
    )

    class Meta:
        model = TutorDisplay
        fields = ("key", "color_bg", "color_txt")


class ModuleDisplayResource(resources.ModelResource):
    module = fields.Field(
        column_name="key", attribute="module", widget=ForeignKeyWidget(Module, "abbrev")
    )

    class Meta:
        model = ModuleDisplay
        fields = ("key", "color_bg", "color_txt")


class ModuleDisplayAdmin(DepartmentModelAdmin):
    list_display = ("module", "color_bg", "color_txt")
    ordering = ("module",)


class TutorDisplayAdmin(DepartmentModelAdmin):
    list_display = ("tutor", "color_bg", "color_txt")
    ordering = ("tutor",)


admin.site.register(BreakingNews, BreakingNewsAdmin)
admin.site.register(TutorDisplay, TutorDisplayAdmin)
admin.site.register(ModuleDisplay, ModuleDisplayAdmin)
