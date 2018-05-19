from testarsenal import DjangoTest
from zinc.templatetags import *

class TimeStringTests(DjangoTest):

    def test_can_convert_positive_values(self):
        self.assertEqual(angstroms(1.1), "1.1 Å")
        self.assertEqual(angstroms(1), "1 Å")


    def test_can_convert_zero_values(self):
        self.assertEqual(angstroms(0), "N/A")
        self.assertEqual(angstroms(None), "N/A")
