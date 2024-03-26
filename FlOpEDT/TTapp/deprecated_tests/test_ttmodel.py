from unittest import skip
from unittest.mock import patch

from django.test import TestCase

import base.models as models
from TTapp.TimetableModel import TimetableModel


def mock_optimize(self, time_limit=300, solver="CBC", presolve=2):
    # mock optimize function
    print("call to mock optimize")
    return True


def mock_add_tt_to_db(target_work_copy):
    pass


class TimetableModelTestCase(TestCase):
    fixtures = ["dump.json"]

    @property
    def week(self):
        return models.Course.objects.exclude(week__nb=None).first().week

    @skip("redondant testting")
    def test_init(self):
        tp1 = models.TrainingProgramme.objects.get(abbrev="INFO1")
        tt = TimetableModel(tp1.department.abbrev, weeks=[self.week], train_prog=tp1)
        self.assertIsNotNone(tt)

    @skip("redondant testting")
    @patch("TTapp.TimetableModel.TimetableModel.optimize", side_effect=mock_optimize)
    @patch(
        "TTapp.TimetableModel.TimetableModel.add_tt_to_db",
        side_effect=mock_add_tt_to_db,
    )
    def test_solve_without_optimize(self, optimize, add_tt_to_db):
        tp1 = models.TrainingProgramme.objects.get(abbrev="INFO1")
        tt = TimetableModel(tp1.department.abbrev, self.week, train_prog=tp1)
        tt.solve(time_limit=300, solver="CBC")
        self.assertTrue(True)

    def test_solve(self):
        tp1 = models.TrainingProgramme.objects.get(abbrev="INFO1")
        tt = TimetableModel(tp1.department.abbrev, self.week, train_prog=tp1)
        tt.solve(time_limit=300, solver="CBC")
        self.assertTrue(True)
