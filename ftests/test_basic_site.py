from time import sleep
from .base import BrowserTest

class BasePageLayoutTests(BrowserTest):

    def test_basic_page_layout(self):
        self.get("/")

        # There is a nav, a main section, and a footer
        body = self.browser.find_element_by_tag_name("body")
        self.assertEqual(
         [element.tag_name for element in body.find_elements_by_xpath("./*")],
         ["header", "nav", "main", "footer"]
        )

        # The header has a logo and a menu icon
        header = body.find_element_by_tag_name("header")
        logo = header.find_element_by_id("logo")
        self.assertEqual(logo.text, "ZincBind")
        menu_icon = header.find_element_by_id("mobile-menu")

        # The nav has a list of nav links
        nav = self.browser.find_element_by_tag_name("nav")
        nav_links = nav.find_elements_by_tag_name("li")
        self.assertGreaterEqual(len(nav_links), 2)

        # The footer has two lists of links, each having at least three
        footer = body.find_element_by_tag_name("footer")
        lists = footer.find_elements_by_class_name("footer-list")
        self.assertGreaterEqual(len(lists), 2)
        for links in lists:
            header = links.find_element_by_class_name("footer-header")
            self.assertGreater(len(links.find_elements_by_tag_name("a")), 2)
        copyright = footer.find_element_by_id("copyright")


    def test_basic_page_css(self):
        self.get("/")

        # The header is correct
        header = self.browser.find_element_by_tag_name("header")
        self.assertGreater(header.size["height"], 50)

        # The nav links are horizontally aranged
        mobile_menu = header.find_element_by_id("mobile-menu")
        self.assertEqual(
         mobile_menu.value_of_css_property("display"),
         "none"
        )
        nav = self.browser.find_element_by_tag_name("nav")
        nav_links = nav.find_elements_by_tag_name("li")
        for index, link in enumerate(nav_links):
            self.assertEqual(link.location["y"], nav_links[0].location["y"])
            if index:
                self.assertGreater(
                 link.location["x"], nav_links[index - 1].location["x"]
                )

        # The footer is at the bottom
        footer = self.browser.find_element_by_tag_name("footer")
        self.assertGreater(footer.location["y"], 500)

        # The footer lists are side by side
        lists = footer.find_elements_by_class_name("footer-list")
        self.assertGreater(lists[1].location["x"], lists[0].location["x"])


    def test_basic_page_css(self):
        self.get("/")

        # The header is correct
        header = self.browser.find_element_by_tag_name("header")
        self.assertGreater(header.size["height"], 50)

        # The nav links are horizontally aranged
        nav = self.browser.find_element_by_tag_name("nav")
        mobile_menu = header.find_element_by_id("mobile-menu")
        self.assertEqual(
         mobile_menu.value_of_css_property("display"),
         "none"
        )
        nav_links = nav.find_elements_by_tag_name("li")
        for index, link in enumerate(nav_links):
            self.assertEqual(link.location["y"], nav_links[0].location["y"])
            if index:
                self.assertGreater(
                 link.location["x"], nav_links[index - 1].location["x"]
                )

        # The footer is at the bottom
        footer = self.browser.find_element_by_tag_name("footer")
        if not self.headless:
            self.assertGreater(footer.location["y"], 500)

        # The footer lists are side by side
        lists = footer.find_elements_by_class_name("footer-list")
        self.assertGreater(lists[1].location["x"], lists[0].location["x"])


    def test_basic_page_mobile_css(self):
        self.browser.set_window_size(350, 600)
        self.get("/")

        # The nav looks correct
        header = self.browser.find_element_by_tag_name("header")
        nav = self.browser.find_element_by_tag_name("nav")
        mobile_menu = header.find_element_by_id("mobile-menu")
        self.assertEqual(
         nav.value_of_css_property("display"),
         "none"
        )
        mobile_menu_icon = mobile_menu.find_element_by_id("mobile-menu-icon")
        self.assertGreater(
         mobile_menu_icon.location["x"],
         300
        )

        # Clicking the icon makes the nav links appear and disappear
        mobile_menu_icon.click()
        self.assertEqual(
         nav.value_of_css_property("display"),
         "block"
        )
        for index, link in enumerate(nav.find_elements_by_tag_name("li")):
            self.assertEqual(link.size["width"], nav.size["width"])
            if index:
                self.assertGreater(
                 link.location["y"],
                 nav.find_elements_by_tag_name("li")[index - 1].location["y"]
                )
        mobile_menu_icon.click()
        sleep(1)
        self.assertEqual(
         nav.value_of_css_property("display"),
         "none"
        )

        # The footer lists are vertically arranged
        footer = self.browser.find_element_by_tag_name("footer")
        lists = footer.find_elements_by_class_name("footer-list")
        self.assertGreater(lists[1].location["y"], lists[0].location["y"])
