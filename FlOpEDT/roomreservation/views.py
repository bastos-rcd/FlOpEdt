from django.shortcuts import render
from rest_framework.reverse import reverse_lazy
from django.contrib.auth.decorators import login_required


@login_required
def RoomReservationsView(request, **kwargs):
    db_data = {'dept': request.department.abbrev, 'api': reverse_lazy('api:api_root', request=request),
               'user_id': request.user.id}
    return render(request, 'roomreservation/index.html', {'json_data': db_data})
