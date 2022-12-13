from django.shortcuts import render

from django.http import HttpResponse

from people.models import Tutor
from base.models import Module, ScheduledCourse
import base.queries as queries
from displayweb.models import TutorDisplay, ModuleDisplay
from displayweb.admin import TutorDisplayResource, ModuleDisplayResource

# Create your views here.
def fetch_rectangle_colors(req, **kwargs):
    week = req.GET.get('week', None)
    year = req.GET.get('year', None)
    work_copy = int(req.GET.get('work_copy', '0'))
    filters = {}
    if req.department.mode.cosmo == 1:
        Display = TutorDisplay.objects.select_related('tutor')
        Resource = TutorDisplayResource
    else:
        Display = ModuleDisplay.objects.select_related('module')
        Resource = ModuleDisplayResource
    if week is None or year is None:
        if req.department.mode.cosmo == 1:
            filters['tutor__in'] = \
                Tutor.objects.filter(departments=req.department)
        else:
            filters['module__in'] = \
                Module.objects.filter(train_prog__department=req.department)
    else:
        scheds = ScheduledCourse.objects.filter(
            course__week__nb=week,
            course__week__year=year,
            course__module__train_prog__department=req.department)\
                .prefetch_related('course__module__train_prog')
        unscheds = queries.get_unscheduled_courses(
            req.department,
            week,
            year,
            work_copy)

        to_be_colored_set = set()
        if req.department.mode.cosmo == 1:
            for sc in scheds.distinct('tutor'):
                to_be_colored_set.add(sc.tutor)
            for usc in unscheds.distinct('tutor'):
                to_be_colored_set.add(usc.tutor)
            filters['tutor__in'] = list(to_be_colored_set)
        else:
            for sc in scheds.distinct('course__module'):
                to_be_colored_set.add(sc.course.module)
            for usc in unscheds.distinct('module'):
                to_be_colored_set.add(usc.module)
            filters['module__in'] = list(to_be_colored_set)
    
    dataset = Resource().export(Display.filter(**filters))
    return HttpResponse(dataset.csv, content_type='text/csv')

    
