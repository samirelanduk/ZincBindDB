from time import sleep
from .base import FunctionalTest

class BasePageLayoutTests(FunctionalTest):

    def test_basic_page_layout(self):
        self.get("/")

        # There is a nav, a main section, and a footer
        body = self.browser.find_element_by_tag_name("body")
        self.assertEqual(
         [element.tag_name for element in body.find_elements_by_xpath("./*")],
         ["nav", "ul", "main", "footer"]
        )

        # The nav has a logo and a list of nav links
        nav = body.find_element_by_tag_name("nav")
        logo = nav.find_element_by_id("logo")
        self.assertEqual(logo.text, "zincDB")
        nav_links = self.browser.find_element_by_id("nav-links")
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


    def test_basic_page_css(self):
        self.get("/")

        # The nav is correct
        nav = self.browser.find_element_by_tag_name("nav")
        self.assertGreater(nav.size["height"], 50)
        self.assertNotEqual(
         nav.value_of_css_property("background-color"), "rgba(0, 0, 0, 0)"
        )

        # The nav links are horizontally aranged
        nav_links = self.browser.find_element_by_id("nav-links")
        mobile_menu = nav.find_element_by_id("mobile-menu")
        self.assertEqual(
         mobile_menu.value_of_css_property("display"),
         "none"
        )
        nav_links = nav_links.find_elements_by_tag_name("li")
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


    def test_basic_page_mobile_css(self):
        self.browser.set_window_size(350, 600)
        self.get("/")

        # The nav looks correct
        nav = self.browser.find_element_by_tag_name("nav")
        nav_links = self.browser.find_element_by_id("nav-links")
        mobile_menu = nav.find_element_by_id("mobile-menu")
        self.assertEqual(
         nav_links.value_of_css_property("display"),
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
         nav_links.value_of_css_property("display"),
         "block"
        )
        for index, link in enumerate(nav_links.find_elements_by_tag_name("li")):
            self.assertEqual(link.size["width"], nav.size["width"])
            if index:
                self.assertGreater(
                 link.location["y"],
                 nav_links.find_elements_by_tag_name("li")[index - 1].location["y"]
                )
        mobile_menu_icon.click()
        sleep(1)
        self.assertEqual(
         nav_links.value_of_css_property("display"),
         "none"
        )

        # The footer lists are vertically arranged
        footer = self.browser.find_element_by_tag_name("footer")
        lists = footer.find_elements_by_class_name("footer-list")
        self.assertGreater(lists[1].location["y"], lists[0].location["y"])



class HomePageTests(FunctionalTest):

    def test_home_page(self):
        self.get("/about/")
        logo = self.browser.find_element_by_id("logo")
        logo.click()

        self.check_page("/")



class AboutPageTests(FunctionalTest):

    def test_about_page(self):
        self.get("/")
        nav_links = self.browser.find_element_by_id("nav-links")
        nav_links.find_elements_by_tag_name("li")[0].click()

        self.check_page("/about/")
        self.assertIn("About", self.browser.title)
        self.assertIn("About", self.browser.find_element_by_tag_name("h1").text)



class HelpPageTests(FunctionalTest):

    def test_help_page(self):
        self.get("/")
        nav_links = self.browser.find_element_by_id("nav-links")
        nav_links.find_elements_by_tag_name("li")[1].click()

        self.check_page("/help/")
        self.assertIn("Help", self.browser.title)
        self.assertIn("Help", self.browser.find_element_by_tag_name("h1").text)



class ChangelogPageTests(FunctionalTest):

    def test_changelog_page(self):
        self.get("/")
        footer = self.browser.find_element_by_tag_name("footer")
        footer.find_elements_by_tag_name("a")[2].click()

        self.check_page("/changelog/")
        self.assertIn("Changelog", self.browser.title)
        self.assertIn("Changelog", self.browser.find_element_by_tag_name("h1").text)
