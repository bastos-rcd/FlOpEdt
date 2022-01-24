
# to fix error message : django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet.
import django
django.setup()
# end
from unittest import skip
from django.test import TestCase
from base.models import Week, Department
from TTapp.TTConstraints.core_constraints import ConsiderTutorsUnavailability
import TTapp.tests.test_pre_analyse.json_response as json_response_module

# Test pre_analyse function for constraints in core_constraints.py : assert correct result returned
class ConsiderTutorsUnavailabilityTestCase(TestCase):

    fixtures = ['data_test_constraints.json']

    def setUp(self):

        # Departments
        self.default_dep = Department.objects.get(abbrev="default")
        self.dep_2 = Department.objects.get(abbrev="Dept2")

        # Constraints by departments
        self.constraint_default_dep = ConsiderTutorsUnavailability.objects.get(department=self.default_dep)
        self.constraint_dep_2 = ConsiderTutorsUnavailability.objects.get(department=self.dep_2)

        # Weeks
        self.week_1_2022 = Week.objects.get(year=2022, nb=1)
        self.week_2_2022 = Week.objects.get(year=2022, nb=2)
        self.week_3_2022 = Week.objects.get(year=2022, nb=3)
        self.week_4_2022 = Week.objects.get(year=2022, nb=4)
        self.week_5_2022 = Week.objects.get(year=2022, nb=5)
        self.week_6_2022 = Week.objects.get(year=2022, nb=6)

    def test_consider_tutor_unavailability(self):
        # Test 1 : KO case : tutor "bibiTU" has 2 courses of 2h to give but only 2h available in his schedule in first week of 2022
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_1_2022)
        self.assertJsonResponseIsKO("1", json_response_dict)

        # Test 2 : OK case : tutor "bibiTU" has 2 courses of 2h to give and 2 days entirely available in 2nd week
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_3_2022)
        self.assertJsonResponseIsOK("2", json_response_dict)

    def test_consider_course_beginning_time(self):
        # Test 3 : KO case : tutor "bibiTU" has 2 courses of 2h to give and only 1 day available in 3rd week.
        #          Both courses must begin at 8o'clock wich implies conflicts.
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_2_2022)
        self.assertJsonResponseIsKO("3", json_response_dict)

    def test_consider_holidays(self):
        # Test 4 : KO case : tutor "prof1" has 4 courses to give, all must begin at 8 o'clock, he does not work on mondays
        #          and wednesday is holiday wich implies conflicts
        json_response_dict = self.constraint_dep_2.pre_analyse(week=self.week_2_2022)
        self.assertJsonResponseIsKO("4", json_response_dict)

        # Test 5 : OK case : tutor "prof1" has 3 courses to give, all must begin at 8 o'clock, he does not work on mondays
        #          and wednesday is holiday
        json_response_dict = self.constraint_dep_2.pre_analyse(week=self.week_3_2022)
        self.assertJsonResponseIsOK("5", json_response_dict)

    def test_consider_tutor_unavailability_in_all_departments(self):
        # Test 6 : KO case : tutor "bibiTU" can work only on tuesday and has 2 courses to give, 1 in each department,
        #          but both can begin only at 8 o'clock, wich lead to a conflict.
        json_response_dict_default_dep = self.constraint_default_dep.pre_analyse(week=self.week_4_2022)
        json_response_dict_dep_2 = self.constraint_dep_2.pre_analyse(week=self.week_4_2022)
        self.assertJsonResponseIsKO("6.1", json_response_dict_default_dep) \
        and self.assertJsonResponseIsKO("6.2", json_response_dict_dep_2)

        # Test 7 : OK case : tutor "bibiTU" can work only on tuesday and thursay and has 2 courses to give, 1 in each department,
        #          both can begin only at 8 o'clock
        json_response_dict_default_dep = self.constraint_default_dep.pre_analyse(week=self.week_6_2022)
        json_response_dict_dep_2 = self.constraint_dep_2.pre_analyse(week=self.week_6_2022)
        self.assertJsonResponseIsOK("7.1", json_response_dict_default_dep) \
        and self.assertJsonResponseIsOK("7.2", json_response_dict_dep_2)

    def test_consider_enough_nb_slots(self):
        # Test 8 : KO case : tutor "bibiTU" works only on tuesday, and has 2 courses to give, they must begin at 8 o'clock
        #          wich is impossible.
        json_response_dict = self.constraint_default_dep.pre_analyse(week=self.week_5_2022)
        self.assertJsonResponseIsKO("8", json_response_dict)

    def test_consider_forbidden_days(self):
        # Test 9 : KO case : tutor "prof1" can not work on monday (forbidden day) and he must give 5 courses
        #          that must begin at 8 o'clock
        json_response_dict = self.constraint_dep_2.pre_analyse(week=self.week_1_2022)
        self.assertJsonResponseIsKO("9", json_response_dict)

        # Test 10 : OK case : tutor "prof1" can not work on monday (forbidden day) and he must give 4 courses
        #           that must begin at 8 o'clock
        json_response_dict = self.constraint_dep_2.pre_analyse(week=self.week_5_2022)
        self.assertJsonResponseIsOK("10", json_response_dict)

    def assertJsonResponseIsOK(self, test_id, response_dict):
        """
                Assert that the json response status given in the dictionnary is "OK".

        :param test_id: A string identifying the test concerned (generally a number).
        :type test_id: str
        :param response_dict: A dictionnary containing the data of the json response returned after launcing the pre_analysis.
        :type response_dict: dict

        """
        json_response_manager = json_response_module.JsonResponse()

        # Json response is OK
        self.assertEquals("OK", json_response_manager.getResponseStatus(response_dict),
                          self.unexpectedResponseErrorMessage(test_id, "OK", "KO"))

    def assertJsonResponseIsKO(self, test_id, response_dict):
        """
                Assert that the json response status given in the dictionnary is "KO" and that "ConsiderTutorsUnavailability"
                belongs to the errors' type.

        :param test_id: A string identifying the test concerned (generally a number).
        :type test_id: str
        :param response_dict: A dictionnary containing the data of the json response returned after launcing the pre_analysis.
        :type response_dict: dict

        """
        json_response_manager = json_response_module.JsonResponse()
        all_blocking_constraints_types = list(map(lambda dico: dico["type"], response_dict["messages"]))

        # Json response is KO and json status "ConsiderTutorsUnavailability" belongs to failure's reasons
        self.assertEquals("KO", json_response_manager.getResponseStatus(response_dict),
                          self.unexpectedResponseErrorMessage(test_id, "KO", "OK")) \
        and self.assertIn("ConsiderTutorsUnavailability", all_blocking_constraints_types,
                          self.constraintNotInJsonResponseErrorMessage(test_id))

    def unexpectedResponseErrorMessage(self, test_id, expected_response, actual_response):
        """
                Generate an error message.

        :param test_id: A string identifying the test concerned (generally a number).
        :type test_id: str
        :type expected_response: str
        :type actual_response: str
        :return: A message describing the error that occured when a json response's status is not the expected status.
        :rtype: str

        """
        return "Test %(test_id)s of ConsiderTutorsUnavailability FAILED.\nUnexpected json response, expected %(expected_response)s but got %(actual_response)s"%{'test_id' : str(test_id),
                                                                                                                                                                 'expected_response' : expected_response,
                                                                                                                                                                 'actual_response' : actual_response}

    def constraintNotInJsonResponseErrorMessage(self, test_id):
        """
                Generate an error message.
                
        :param test_id: A string identifying the test concerned (generally a number).
        :type test_id: str

        :return: A message describing the error that occured when a json response's set of errors' type does not contain the expected type ConsiderTutorsUnavailability.
        :rtype: str

        """
        return "Test %(test_id)s of ConsiderTutorsUnavailability FAILED.\nExpected ConsiderTutorsUnavailability in failure's reasons."%{'test_id' : str(test_id)}

# TODO : delete at the end, only print tests
if __name__ == "__main__":
    tc = ConsiderTutorsUnavailabilityTestCase()
    # holidays
    my_week = Week.objects.get(year=2022, nb=2)
    dep = Department.objects.get(abbrev="Dept2")
    print(dep)
    constraint_holidays = ConsiderTutorsUnavailability.objects.get(department=dep)
    print(constraint_holidays)
    constraint_holidays.pre_analyse(week=my_week)
    # end holidays
    #tc.assertTrue(False, tc.unexpectedResponseErrorMessage("3", "KO", "OK"))
    #tc.assertTrue(False, tc.constraintNotInJsonResponseErrorMessage("3"))
    '''cs = ConsiderTutorsUnavailability.objects.all()
    my_week = Week.objects.get(year=2022, nb=2)
    print(Department.objects.all())
    dep = list(map(lambda dep: dep.abbrev, Department.objects.all()))
    for dep_abbrev in dep:
        for c in cs:
            if c.department.abbrev == dep_abbrev:
                print("## DEP :", c.department)
                json_response_dict = c.pre_analyse(week=my_week)
                print(json_response_dict)

                jrobject = json_response_module.JsonResponse()
                types = list(map(lambda dico: dico["type"], json_response_dict["messages"]))
                print("## TYPES :",types)
'''
