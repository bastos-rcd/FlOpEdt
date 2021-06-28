from django.urls import reverse
from rest_framework.test import APIClient, APITestCase, APIRequestFactory
from base.models import Department, TrainingProgramme
from django.utils.http import urlencode
from TTapp.TTConstraints import tutors_constraints, visio_constraints


def urlreverse(viewname, kwargs=None, query_kwargs=None):
    url = reverse(viewname, kwargs=kwargs)

    if query_kwargs:
        return f'{url}?{urlencode(query_kwargs)}'

    return(url)


class DepartmentTest(APITestCase):
    def setUp(self):
        Department.objects.create(name="Informatique", abbrev="INFO")
        Department.objects.create(name='Reseaux et Telecommunications', abbrev="RT")

    def test_get_department(self):
        url=reverse('api:fetch:dept-list')

        response = self.client.get(url)

        self.assertEqual(len(response.json()), 2)
        self.assertEqual(Department.objects.first().name, "Informatique")

class TrainingProgrammeTest(APITestCase):
    def setUp(self):
        deptinfo = Department.objects.create(name="Informatique", abbrev="INFO")
        deptrt = Department.objects.create(name='Reseaux et Telecommunications', abbrev="RT")

        TrainingProgramme.objects.create(name="Informatique 1er année", abbrev="INFO1", department=deptinfo)
        TrainingProgramme.objects.create(name="Informatique 2eme année", abbrev="INFO2", department=deptinfo)

        TrainingProgramme.objects.create(name="Reseaux et Telecommunications 1er année", abbrev="RT1", department=deptrt)
        TrainingProgramme.objects.create(name="Reseaux et Telecommunications 2eme année", abbrev="RT2", department=deptrt)
        
    def test_get_TrainingProgramme(self):
        url = urlreverse('api:base:trainingprogramme-name-list', query_kwargs={'dept':'INFO'})

        response = self.client.get(url)
        
        self.assertEqual(len(response.json()), 2)
    
class ConstraintTest(APITestCase):
    def setUp(self):
        tutors_constraints.MinTutorsHalfDays.objects.create()
        tutors_constraints.MinNonPreferedTutorsSlot.objects.create()
        visio_constraints.NoVisio.objects.create()

    def test_get_constraint(self):
        url = '/en/api/ttapp/constraint/' 

        response = self.client.get(url)

        self.assertEqual(len(response.json()), 3)
