from selenium.common.exceptions import StaleElementReferenceException
from .base import FunctionalTest

class HomePageTests(FunctionalTest):

    def test_home_page_layout(self):
        # They go to the home page
        self.get("/")
        self.check_title("ZincBind")

        # There is a nav bar
        nav = self.browser.find_element_by_tag_name("nav")
        self.assertIn("ZincBind", nav.text)
        nav_links = nav.find_element_by_id("nav-links")
        nav_links = nav_links.find_elements_by_tag_name("a")
        self.assertGreaterEqual(len(nav_links), 3)

        # There is a site description
        description = self.browser.find_element_by_id("site-description")
        self.assertIn("database of zinc binding sites", description.text.lower())

        # The logo leads back to the home page
        logo = nav.find_element_by_id("logo")
        self.click(logo)
        with self.assertRaises(StaleElementReferenceException):
            nav.find_element_by_tag_name("a")
