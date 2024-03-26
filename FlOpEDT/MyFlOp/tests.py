
from unittest import mock

from django.test import TestCase

from base.models import Department
from MyFlOp.MyTimetableUtils import reassign_rooms, swap_version


def mock_tt_method(self, *args, **kwargs):
    pass

class MyTimetableUtilsTestCase(TestCase):

    def setUp(self):
        self.department = Department.objects.create(name="departement1", abbrev="dept1")

    @mock.patch('MyFlOp.MyTimetableUtils.basic_swap_version')
    def test_department_abbrev_on_swap_version(self, basic_swap_version):
        self.assertIsInstance(basic_swap_version, mock.MagicMock)
        swap_version(self.department.abbrev, 39, 2018, 0, 0)
        self.assertTrue(basic_swap_version._called_with(self.department, 39, 2018, 0, 0))

    @mock.patch('MyFlOp.MyTimetableUtils.basic_swap_version')
    def test_department_instance_on_swap_version(self, basic_swap_version):
        self.assertIsInstance(basic_swap_version, mock.MagicMock)
        swap_version(self.department, 39, 2018, 0, 0)
        self.assertTrue(basic_swap_version._called_with(self.department, 39, 2018, 0, 0))

    @mock.patch('MyFlOp.MyTimetableUtils.basic_swap_version')
    def test_swap_version_department_key_error(self, basic_swap_version):
        with self.assertRaises(Department.DoesNotExist):     
            swap_version('no_dept', 39, 2018, 0, 0)            
        self.assertFalse(basic_swap_version.called)
