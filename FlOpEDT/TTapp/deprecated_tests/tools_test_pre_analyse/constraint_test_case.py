from django.test import TestCase

import TTapp.deprecated_tests.tools_test_pre_analyse.json_response as json_response_module


class ConstraintTestCase(TestCase):
    """
        A class that inherits from Django TestCase class. Is intended to be inherited. Allow to compare a dictionary
        (json response) with an expected result given.
        Note : it is important to define with a string the property `contraint_type` with the setUp method.

    """

    def setUp(self):
        self.constraint_type = None

    def assertJsonResponseIsOK(self, test_id, response_dict):
        """
                Assert that the json response status given in the dictionary is "OK".

        :param test_id: A string identifying the test concerned (generally a number).
        :type test_id: str
        :param response_dict: A dictionary containing the data of the json response returned after launching the pre_analysis.
        :type response_dict: dict

        """
        if self.constraint_type is not None:

            # Json response is OK
            self.assertEquals("OK", json_response_module.getResponseStatus(response_dict),
                          self.unexpectedResponseErrorMessage(test_id, "OK", "KO"))

        else:
            print("Constraint's type is not set up while ConstraintTestCase inheritance.")

    def assertJsonResponseIsKO(self, test_id, response_dict):
        """
                Assert that the json response status given in the dictionary is "KO" and that the constraint's type belongs to the errors' type.

        :param test_id: A string identifying the test concerned (generally a number).
        :type test_id: str
        :param response_dict: A dictionary containing the data of the json response returned after launching the pre_analysis.
        :type response_dict: dict

        """
        if self.constraint_type is not None:
            all_blocking_constraints_types = list(map(lambda dico: dico["type"], response_dict["messages"]))

            # Json response is KO and constraint's type belongs to failure's reasons
            self.assertEquals("KO", json_response_module.getResponseStatus(response_dict),
                              self.unexpectedResponseErrorMessage(test_id, "KO", "OK")) \
            and self.assertIn(self.constraint_type, all_blocking_constraints_types,
                              self.constraintNotInJsonResponseErrorMessage(test_id))
        else:
            print("Constraint's type is not set up while ConstraintTestCase inheritance.")


    def unexpectedResponseErrorMessage(self, test_id, expected_response, actual_response):
        """
                Generate an error message.

        :param test_id: A string identifying the test concerned (generally a number).
        :type test_id: str
        :type expected_response: str
        :type actual_response: str
        :return: A message describing the error that occurred when a json response's status is not the expected status.
        :rtype: str

        """
        return "Test %(test_id)s of %(constraint_type)s FAILED.\nUnexpected json response, expected %(expected_response)s but got %(actual_response)s"%{'test_id' : str(test_id),
                                                                                                                                                        'constraint_type' : self.constraint_type,
                                                                                                                                                        'expected_response' : expected_response,
                                                                                                                                                        'actual_response' : actual_response}

    def constraintNotInJsonResponseErrorMessage(self, test_id):
        """
                Generate an error message.

        :param test_id: A string identifying the test concerned (generally a number).
        :type test_id: str

        :return: A message describing the error that occurred when a json response's set of errors' type does not contain the expected type ConsiderTutorsUnavailability.
        :rtype: str

        """
        return "Test %(test_id)s of %(constraint_type)s FAILED.\nExpected %(constraint_type)s in failure's reasons."%{'test_id' : str(test_id),
                                                                                                                      'constraint_type' : self.constraint_type}