from time import sleep
from zincsites.models import Pdb, Residue, ZincSite
from .base import FunctionalTest

class SiteDisplayTest(FunctionalTest):

    def setUp(self):
        FunctionalTest.setUp(self)
        pdb1 = Pdb.objects.create(
         id="P111", deposition_date="2016-10-11",
         title="A TEST PDB OF THE FIRST KIND"
        )
        pdb2 = Pdb.objects.create(
         id="P222", deposition_date="2014-10-11",
         title="A TEST PDB OF THE SECOND KIND"
        )
        pdb3 = Pdb.objects.create(
         id="P333", deposition_date="2013-10-11",
         title="A TEST PDB OF THE THIRD KIND"
        )
        site1 = ZincSite.objects.create(id="P111A400")
        site2 = ZincSite.objects.create(id="P222A400")
        site3 = ZincSite.objects.create(id="P222A500")
        site4 = ZincSite.objects.create(id="P333A400")
        site5 = ZincSite.objects.create(id="P444A500")



class ZincSiteListTests(SiteDisplayTest):

    def test_can_get_list(self):
        self.get("/")

        # There is a link to zinc sites in the header
        nav_links = self.browser.find_element_by_id("nav-links")
        nav_links.find_elements_by_tag_name("li")[0].click()

        self.check_page("/sites/")
        self.check_title("All Zinc Sites")
        self.check_h1("All Zinc Sites")

        # There is a table with sufficient rows
        table = self.browser.find_element_by_tag_name("table")
        rows = table.find_elements_by_tag_name("tr")
        self.assertEqual(len(rows), 6)

        # The IDs are in the first column
        self.assertEqual(rows[0].find_element_by_tag_name("td").text, "5O8HA501")
        self.assertEqual(rows[1].find_element_by_tag_name("td").text, "P111A400")
        self.assertEqual(rows[2].find_element_by_tag_name("td").text, "P222A400")
        self.assertEqual(rows[3].find_element_by_tag_name("td").text, "P222A500")
        self.assertEqual(rows[4].find_element_by_tag_name("td").text, "P333A400")
        self.assertEqual(rows[5].find_element_by_tag_name("td").text, "P444A500")

        # Clicking them takes you to the right page
        rows[0].find_element_by_tag_name("a").click()
        self.check_page("/sites/5O8HA501/")
        self.check_site_page(
         "5O8H", "11 October, 2017", "CRYSTAL STRUCTURE OF R. RUBER",
         ["A92", "A95", "A98"], ["CYS", "CYS", "CYS"]
        )
        self.browser.back()
        self.check_page("/sites/")
