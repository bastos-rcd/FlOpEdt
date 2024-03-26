from django.shortcuts import render
from django.template.response import TemplateResponse

from base.views import clean_edt_view_params
from base.weeks import week_list


# Create your views here.
def manager(req, **kwargs):
    week, year = clean_edt_view_params(None, None)

    return TemplateResponse(req, 'cstmanager/index.html', {
        'dept': req.department.abbrev,
        'all_weeks': week_list(),
        'week': week,
        'year': year,
    })
