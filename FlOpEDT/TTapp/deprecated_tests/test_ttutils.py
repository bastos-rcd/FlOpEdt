from django.test import TestCase
from TTapp.TTUtils import basic_swap_version, basic_reassign_rooms
import base.models as models

class TTutilsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.department1 = models.Department.objects.create(name="departement1", abbrev="dept1")
        cls.department2 = models.Department.objects.create(name="departement2", abbrev="dept2")
        cls.tp1 = models.TrainingProgramme.objects.create(name="TrainingProgramme1", abbrev="tp1", department=cls.department1)
        cls.tp2 = models.TrainingProgramme.objects.create(name="TrainingProgramme2", abbrev="tp2", department=cls.department2)
        cls.gt1 = models.GroupType.objects.create(name="group_type_1", department=cls.department1)
        cls.g1 = models.StructuralGroup.objects.create(name="gp1", train_prog=cls.tp1, type=cls.gt1, size=0)
        cls.ct1 = models.CourseType.objects.create(name="CourseType1")
        cls.m1 = models.Module.objects.create(name="module1", abbrev="m1", train_prog=cls.tp1, period=cls.p1)
        cls.p1 = models.TrainingPeriod.objects.create(
            name="annee_complete", starting_week=0, ending_week=53
        )
        cls.w1 = models.Week.objects.create(nb=39, year=2019)
        cls.c1 = models.Course.objects.create(week=cls.w1, type=cls.ct1, module=cls.m1)
        cls.c1.groups.add(cls.g1)
        cls.day1 = models.Day.MONDAY
        cls.edtv1 = models.EdtVersion.objects.create(department=cls.department1, week=cls.w1, version=3)
        cls.scheduled_courses = {}
        for i in range(0,9):
            cls.scheduled_courses[i] = models.ScheduledCourse.objects.create(course=cls.c1,
                                                                             start_time=480,
                                                                             day=cls.day1,
                                                                             work_copy=i)

    def test_basic_swap_version(self):
        basic_swap_version(self.department1, self.w1, 2, 5)
        edt_version = models.EdtVersion.objects.get(department=self.department1, week=self.w1)
        self.assertEqual(edt_version.version, 4)
        
        for sc in self.scheduled_courses.values():
            sc.refresh_from_db()

        self.assertEqual(self.scheduled_courses[2].work_copy, 5)
        self.assertEqual(self.scheduled_courses[5].work_copy, 2)

    def test_basic_reassign_rooms(self):
        basic_reassign_rooms(self.department1, self.w1, 0)
        self.assertTrue(True)