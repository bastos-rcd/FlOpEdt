from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse


@login_required
def room_reservations_view(request, **kwargs):
    db_data = {
        "dept": request.department.abbrev,
        "api": reverse("api:api_root"),
        "user_id": request.user.id,
    }
    return render(request, "roomreservation/index.html", {"json_data": db_data})
