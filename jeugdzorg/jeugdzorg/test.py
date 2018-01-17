from django.test import TestCase


class TestTests(TestCase):
    def setUp(self):
        self.a = 'ok'
        self.b = 'ok'

    def test_tests(self):
        self.assertEqual(self.a, self.b)

