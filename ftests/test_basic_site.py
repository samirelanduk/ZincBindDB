from time import sleep
from .base import FunctionalTest

class BasePageLayoutTests(FunctionalTest):

    def test_basic_page_layout(self):
        self.get("/")

        # There is a nav, a main section, and a footer
        body = self.browser.find_element_by_tag_name("body")
        self.assertEqual(
         [element.tag_name for element in body.find_elements_by_xpath("./*")],
         ["nav", "main", "footer"]
        )

        # The nav has a logo and a list of nav links
        nav = body.find_element_by_tag_name("nav")
        logo = nav.find_element_by_id("logo")
        self.assertEqual(logo.text, "zincDB")
        nav_links = nav.find_element_by_id("nav-links")
        nav_links = nav_links.find_elements_by_tag_name("li")
        self.assertGreaterEqual(len(nav_links), 2)

        # The footer has two lists of links, each having at least three
        footer = body.find_element_by_tag_name("footer")
        lists = footer.find_elements_by_class_name("footer-list")
        self.assertGreaterEqual(len(lists), 2)
        for links in lists:
            header = links.find_element_by_class_name("footer-header")
            self.assertGreater(len(links.find_elements_by_tag_name("a")), 2)
        copyright = footer.find_element_by_id("copyright")
