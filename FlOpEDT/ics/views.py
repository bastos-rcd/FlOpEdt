from django.shortcuts import render

from people.models import Tutor
from base.models import Group, Room
import base.queries as queries

def index(request, **kwargs):
    enseignant_list = Tutor.objects.filter(is_active=True, is_tutor=True).order_by('username')
    group_list = Group.objects.filter(basic=True,
                                       train_prog__department=request.department)\
                               .order_by('train_prog__abbrev', 'name')
    salle_list = [n.name.replace(' ','_') for n in queries.get_rooms(None, basic=True).order_by('name')]
    context = {'enseignants': enseignant_list,
               'groupes':group_list,
               'salles':salle_list,
               'requi':request.build_absolute_uri()[:-1]}
    return render(request, 'ics/index.html', context=context)
