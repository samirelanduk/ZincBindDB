from time import sleep
from .base import FunctionalTest

class SiteDisplayTest(FunctionalTest):

    def setUp(self):
        FunctionalTest.setUp(self)


class ZincSiteListTests(FunctionalTest):

    def test_can_get_list(self):
        self.get("/")

        # There is a link to zinc sites in the header
        nav_links = self.browser.find_element_by_id("nav-links")
        nav_links.find_elements_by_tag_name("li")[0].click()

        self.check_page("/sites/")
        self.check_title("All Zinc Sites")
        self.check_h1("All Zinc Sites")
