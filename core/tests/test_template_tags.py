from testarsenal import DjangoTest
from core.templatetags import *

class AngstromConverterTests(DjangoTest):

    def test_can_convert_positive_values(self):
        self.assertEqual(angstroms(1.1), "1.1 Å")
        self.assertEqual(angstroms(1), "1 Å")


    def test_can_convert_zero_values(self):
        self.assertEqual(angstroms(0), "N/A")
        self.assertEqual(angstroms(None), "N/A")



class PagificationTests(DjangoTest):

    def test_can_add_page_url(self):
        self.assertEqual(
         pagify("www.samireland.com?x=y&p=12", 2),
         "www.samireland.com?x=y&p=12&page=2"
        )
        

    def test_can_update_page_url(self):
        self.assertEqual(
         pagify("www.samireland.com?x=y&p=12&page=19", 2),
         "www.samireland.com?x=y&p=12&page=2"
        )
