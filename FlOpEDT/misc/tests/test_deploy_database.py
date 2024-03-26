import os

from django.test import TestCase
from openpyxl import load_workbook

from base.models import Department, TimeGeneralSettings
from configuration.deploy_database import convert_time, settings_extract


class ExtractGeneralSettingsTestCase(TestCase):

    def setUp(self):
        dirname = os.path.dirname(__file__)
        bookname = '../deploy_database/database_file_iut.xlsx'
        filename = os.path.join(dirname, bookname)

        # Test department existence
        self.department, _ = Department.objects.get_or_create(
            name='department test', abbrev='test')
        self.book = load_workbook(filename, data_only=True)

    def test_convert_time(self):
        time = convert_time('02:35:00')
        self.assertEqual(time, 155)

    def test_extract_settings(self):
        settings_extract(self.department, self.book)
        ts = TimeGeneralSettings.objects.get(department=self.department)
        self.assertIsNotNone(ts)
