from django.db.models import Q
from django.shortcuts import render

import base.queries as queries
from base.models import Department, StructuralGroup, TransversalGroup
from people.models import Tutor


def index(request, **kwargs):
    tutor_list = (
        Tutor.objects.filter(
            is_active=True, is_tutor=True, departments=request.department
        )
        .prefetch_related("departments")
        .order_by("username")
    )
    structural_group_list = (
        StructuralGroup.objects.filter(
            basic=True, train_prog__department=request.department
        )
        .select_related("train_prog__department")
        .order_by("train_prog__abbrev", "name")
    )
    transversal_group_list = (
        TransversalGroup.objects.filter(train_prog__department=request.department)
        .select_related("train_prog__department")
        .order_by("train_prog__abbrev", "name")
    )
    room_list = [
        {"name": n.name, "id": n.id}
        for n in queries.get_rooms(request.department.abbrev, basic=True).order_by(
            "name"
        )
    ]
    deps = Department.objects.all()
    # We consider suffix length to avoid ics link representation
    # suffix_length = len(request.department.abbrev) + 9
    context = {
        "tutors": tutor_list,
        "structural_groups": structural_group_list,
        "transversal_groups": transversal_group_list,
        "rooms": room_list,
        "deps": deps,
        # 'requi': request.build_absolute_uri()[:-suffix_length]
    }
    return render(request, "flop_ics/index.html", context=context)
