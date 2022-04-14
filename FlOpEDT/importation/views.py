from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from django.db import transaction

import os

from core.decorators import superuser_required

from base.models import Period, Department

from configuration.forms import ImportFile
from configuration.file_manipulation import check_ext_file, upload_file

from importation.csv_reader import csv_reader
from importation.make_dispo_file import make_dispo_file
from importation.translate_to_csv import convert_xlsx2csv


@superuser_required
def importation_dispo(req, **kwargs):
    try:
        department = Department.objects.get(abbrev=kwargs['department'])
    except:
        return "Erreur departement"
    periods = [p.name for p in Period.objects.filter(department=department)]
    form = ImportFile()
    if req.method == 'POST':
        form = ImportFile(req.POST, req.FILES)
        if form.is_valid():
            if check_ext_file(req.FILES['file'], ['.xlsx', '.xls']):
                path = upload_file(req.FILES['file'], "importation/dispo_.xlsx")
                csv_path = convert_xlsx2csv(path, target_path=f"{settings.MEDIA_ROOT}/importation/dispo_file_.csv")
            elif check_ext_file(req.FILES['file'], ['.csv']):
                csv_path = upload_file(req.FILES['file'], "importation/dispo_file_.csv")
            else:
                error = "pas .xlsx"
            if csv_path:
                try:
                    with transaction.atomic():
                        csv_reader(csv_path)
                        error = "OK"
                        print("CSV OK")
                except Exception as e:
                    error = e
                os.remove(csv_path)
                print("Removing OK")
        else:
            error = "formulaire non valide"
        return render(req, 'importation/importation.html', {'form': form, 'periods': periods, 'ERROR': error})
    return render(req, 'importation/importation.html', {'form': form, 'periods': periods})


@superuser_required
def get_dispo_file(req, period, **kwargs):
    print(period)
    try:
        department = Department.objects.get(abbrev=kwargs['department'])
        period = Period.objects.get(name=period, department=department)
    except:
        return "Erreur nom du departement ou periode"
    path = f"{settings.MEDIA_ROOT}/importation/periods_dispo/dispo_file_{period.name}.xlsx"
    if not os.path.exists(path):
        print("OK")
        path = make_dispo_file(period,
                               empty_bookname=f"{settings.MEDIA_ROOT}/importation/base/empty_dispo_file.xlsx",
                               target_bookname=path)
    f = open(path, "rb")
    response = HttpResponse(f, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f"attachment; filename=\"dispo_file_{period.name}.xlsx\""
    f.close()
    return response

