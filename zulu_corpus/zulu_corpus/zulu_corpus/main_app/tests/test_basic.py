from django.test import TestCase

class BasicTest(TestCase):
    def test_one_plus_one(self):
        self.assertEqual(1 + 1, 2)