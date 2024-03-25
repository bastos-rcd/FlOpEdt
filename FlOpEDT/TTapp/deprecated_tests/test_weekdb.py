import base.models as models

from django.test import TestCase
from TTapp.TimetableModel import TimetableData


class WeekDBTestCase(TestCase):

    fixtures = ["dump.json"]

    def test_attributes(self):
        tp1 = models.TrainingProgramme.objects.get(abbrev="INFO1")
        department1 = tp1.department
        data = TimetableData(department1, 39, 2018, [tp1])
        self.assertEqual(data.train_prog, [tp1])
        # self.assertEqual(list(data.room_groups_for_type[self.rt1]), [self.rg1])
