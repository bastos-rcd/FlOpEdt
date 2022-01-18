
# to fix error message : django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet.
import django
django.setup()
# end
from unittest import skip
from django.test import TestCase
from base.models import Week
from TTapp.TTConstraints.core_constraints import ConsiderTutorsUnavailability
import TTapp.tests.test_pre_analyse.json_response as json_response_module

# Test pre_analyse function for constraints in core_constraints.py : assert correct result returned
class ConsiderTutorsUnavailabilityTestCase(TestCase):

    fixtures = ['data_test_constraints.json']

    def setUp(self):
        self.all_constraints = ConsiderTutorsUnavailability.objects.all()
        self.week_1_2022 = Week.objects.get(year=2022, nb=1)
        self.week_2_2022 = Week.objects.get(year=2022, nb=2)
        self.week_3_2022 = Week.objects.get(year=2022, nb=3)

    def test_consider_tutor_unavailability(self):
        # Test 1 : KO case : tutor has 2 courses of 2h to give but only 2h available in his schedule in first week of 2022
        for constraint in self.all_constraints:
            json_response_dict = constraint.pre_analyse(week=self.week_1_2022)
            self.assertJsonResponseIsExpectedResponse(json_response_dict, "KO")

        # Test 2 : OK case : tutor has 2 courses of 2h to give and 2 days entirely available in 2nd week
        for constraint in self.all_constraints:
            json_response_dict = constraint.pre_analyse(week=self.week_3_2022)
            self.assertJsonResponseIsExpectedResponse(json_response_dict, "OK")

    @skip
    def test_consider_course_beginning_time(self):
        # TODO : must pass
        # Test 3 : KO case : tutor has 2 courses of 2h to give and only 1 day available in 3rd week.
        #          Both courses must begin a 8o'clock witch implies conflicts.
        for constraint in self.all_constraints:
            json_response_dict = constraint.pre_analyse(week=self.week_2_2022)
            self.assertJsonResponseIsExpectedResponse(json_response_dict, "KO")

    def assertJsonResponseIsExpectedResponse(self, response_dict, expected_response):
        json_response_manager = json_response_module.JsonResponse()
        all_blocking_constraints_types = list(map(lambda dico: dico["type"], response_dict["messages"]))

        # Json response is what expected and json status "ConsiderTutorsUnavailability" belongs to the reasons of fail
        self.assertEquals(expected_response, json_response_manager.getResponseStatus(response_dict)) \
        and self.assertIn("ConsiderTutorsUnavailability", all_blocking_constraints_types)

    #def unexpectedResponseErrorMessage(self, test_id, expected_response, actual_response):
    #    return "Test", test_id, "of ConsiderTutorsUnavailability FAILED.\nUnexpected json response, expected", expected_response, "but got", actual_response


# TODO : delete at the en, only print tests
if __name__ == "__main__":
    cs = ConsiderTutorsUnavailability.objects.all()
    my_week = Week.objects.get(year=2022, nb=1)
    for c in cs:
        json_response_dict = c.pre_analyse(week=my_week)
        print(json_response_dict)

        jrobject = json_response_module.JsonResponse()
        types = list(map(lambda dico: dico["type"], json_response_dict["messages"]))
        print("## TYPES :",types)

