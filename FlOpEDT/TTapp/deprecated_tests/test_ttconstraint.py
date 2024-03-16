
from django.test import TestCase
from unittest.mock import patch, Mock, MagicMock, call

from base.models import Department, TrainingProgramme, Course, CourseType, Time
from people.models import Tutor
from TTapp.models import LimitTimePerPeriod, MinHalfDays, CustomConstraint
from TTapp.TimetableModel import TimetableModel


class TimetableConstraintTestCase(TestCase):

    fixtures = ['dump.json']


    def setUp(self):

        self.info = Department.objects.get(abbrev="info")

        self.dut1 = TrainingProgramme.objects.get(abbrev='INFO1')
        self.dut2 = TrainingProgramme.objects.get(abbrev='INFO2')

        self.DS = CourseType.objects.get(name='CTRL')
        self.CM = CourseType.objects.get(name='CM')
        self.TD = CourseType.objects.get(name='TD')
        self.TP = CourseType.objects.get(name='TP')

        self.c_basic = LimitTimePerPeriod.objects.create(limit=1, type=self.TD, department=self.info)

        self.c_2018 = LimitTimePerPeriod.objects.create(train_prog=self.dut1, year=2018, limit=1, type=self.TD, department=self.info)
        self.c_2018_39 = LimitTimePerPeriod.objects.create(train_prog=self.dut1, year=2018, week=39, limit=0, type=self.TD, department=self.info)
        self.c_2018_39_without_tp = LimitTimePerPeriod.objects.create(year=2018, week=39, limit=0, type=self.TD, department=self.info)

        self.c_tp2 = LimitTimePerPeriod.objects.create(train_prog=self.dut2, limit=0, type=self.TD, department=self.info)
        self.c_2019_1 = LimitTimePerPeriod.objects.create(train_prog=self.dut2, year=2019, week=1, limit=0, type=self.TD, department=self.info)


    def test_constraint_without_training_program(self):   
        view_model = self.c_2018_39_without_tp.get_viewmodel()
        self.assertEqual(view_model['details']['train_prog'], 'All')


    @patch('TTapp.models.LimitCourseTypePerPeriod.register_expression')
    def test_limit_register_expression_without_tutors(self, register_expression):      

        attrs = {'wdb.days': (0,1,2,)}
        ttmodel = Mock(**attrs)

        period_by_day = [
            (0, Time.AM),
            (0, Time.PM),
            (1, Time.AM),
            (1, Time.PM),
            (2, Time.AM),
            (2, Time.PM),            
            ]

        calls = [call(ttmodel, period_by_day, 1.),]

        constraint = LimitTimePerPeriod.objects.create(limit=1, type=self.TD, department=self.info)
        constraint.period == LimitTimePerPeriod.FULL_DAY
        constraint.enrich_ttmodel(ttmodel)

        register_expression.assert_has_calls(calls)


    @patch('TTapp.models.LimitCourseTypePerPeriod.register_expression')
    def test_limit_register_expression_with_tutors(self, register_expression):      

        constraint = LimitTimePerPeriod.objects.create(limit=1, type=self.TD, department=self.info)
        constraint.period == LimitTimePerPeriod.FULL_DAY

        calls = []
        attrs = {'wdb.days': (0,1,2,)}
        ttmodel = Mock(**attrs)

        period_by_day = [
            (0, Time.AM),
            (0, Time.PM),
            (1, Time.AM),
            (1, Time.PM),
            (2, Time.AM),
            (2, Time.PM),            
            ]

        for tutor in Tutor.objects.filter(username__in=['AB', 'AJ', 'CDU', 'FMA']):
            calls.append(call(ttmodel, period_by_day, 1., tutor=tutor))
            constraint.tutors.add(tutor)

        constraint.enrich_ttmodel(ttmodel)
        register_expression.assert_has_calls(calls)

    @patch('TTapp.models.ReasonableDays.register_expression')
    def test_reasonable_register_expression_with_tutors(self, register_expression):
        pass

    @patch('TTapp.helpers.minhalfdays.MinHalfDaysHelperTutor.enrich_model')
    def test_minhalfdayshelpertutor(self, enrich_model):

        ttmodel = Mock()

        # Ensure enrich_model has been called with correct tutor
        calls = []
        constraint = MinHalfDays.objects.create(department=self.info)
        for tutor in Tutor.objects.filter(username__in=['AB', 'AJ', 'CDU', 'FMA']):
            calls.append(call(tutor=tutor))
            constraint.tutors.add(tutor)

        constraint.enrich_ttmodel(ttmodel)
        enrich_model.assert_has_calls(calls)


class CustomConstraintTestCase(TestCase):

    @patch('MyFlOp.custom_constraints.FirstCustomConstraint', create=True)
    @patch('TTapp.models.CustomConstraint.class_name', 'MyFlOp.custom_constraints.FirstCustomConstraint')
    def test_get_constraint(self, target_class):
        custom_constraint = CustomConstraint()
        constraint = custom_constraint.get_constraint('MyFlOp.custom_constraints.FirstCustomConstraint')
        self.assertIs(constraint, target_class())

    
    @patch('MyFlOp.custom_constraints.FirstCustomConstraint', create=True)
    @patch('TTapp.models.CustomConstraint.class_name', 'MyFlOp.custom_constraints.FirstCustomConstraint')
    def test_enrich_model(self, constraint_class):
        custom_constraint = CustomConstraint.objects.create(class_name='MyFlOp.custom_constraints.FirstCustomConstraint')
        custom_constraint.enrich_ttmodel(None)
        constraint_instance = constraint_class()
        constraint_instance.enrich_ttmodel.assert_called_once_with(None, 1)
