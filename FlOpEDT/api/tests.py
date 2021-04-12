from django.test import TestCase, Client

import unittest

class APITestCase(TestCase):

    # fixtures = ['dump_post_refactor.json']

    def setUp(self):
        self.client = Client()
