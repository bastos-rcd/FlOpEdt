from base.models import (Course, CourseAvailability, CourseModification,
                         Department, Dependency, GenericGroup, Module,
                         Room, RoomAvailability, RoomSort, ScheduledCourse, StructuralGroup,
                         TrainingHalfDay, TransversalGroup, UserAvailability)
from people.models import Tutor


def get_model_department_lookup(model, department, field_name=None):
    """
    Get filter to apply for department filtering
    of model instances depending on their fields
    """
    lookup = None

    # Look for a direct relation with Department model
    for field in model._meta.get_fields():
        if (
            not field.auto_created
            and field.related_model
            and field.related_model == Department
        ):
            if hasattr(field, "many_to_one") and field.many_to_one:
                lookup = field.name
                break

    if not lookup:
        # Look for a predefined lookup path
        lookups_by_model = {
            Course: "type__department",
            CourseModification: "course__type__department",
            CourseAvailability: "train_prog__department",
            ScheduledCourse: "course__type__department",
            Dependency: "course1__type__department",
            Module: "train_prog__department",
            StructuralGroup: "train_prog__department",
            TransversalGroup: "train_prog__department",
            GenericGroup: "train_prog__department",
            Room: "departments",
            RoomAvailability: "room__subroom_of__types__department",
            RoomSort: "for_type__department",
            TrainingHalfDay: "train_prog__department",
            Tutor: "departments",
            UserAvailability: "user__departments",
        }

        lookup = lookups_by_model.get(model, None)

    if lookup:
        if field_name:
            lookup_name = f"{field_name}__{lookup}"
        else:
            lookup_name = lookup

        return {lookup_name: department}

    return {}
