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
        self.assertIn("7 PDB files", description.text)
        self.assertIn("3 unique", description.text)
        self.assertIn("9 representative", description.text)

        # There is a search bar
        search = self.browser.find_element_by_id("site-search")
        search_form = search.find_element_by_tag_name("form")
        inputs = search_form.find_elements_by_tag_name("input")
        self.assertEqual(len(inputs), 2)

        # The logo leads back to the home page
        logo = nav.find_element_by_id("logo")
        self.click(logo)
        with self.assertRaises(StaleElementReferenceException):
            nav.find_element_by_tag_name("a")

        # There is a footer
        footer = self.browser.find_element_by_tag_name("footer")
        self.assertEqual(len(footer.find_elements_by_tag_name("a")), 6)



class AboutPageTests(FunctionalTest):

    def test_about_page_layout(self):
        # They go to the about page
        self.get("/")
        nav = self.browser.find_element_by_tag_name("nav")
        nav_links = nav.find_element_by_id("nav-links")
        self.click(nav_links.find_element_by_link_text("About"))
        self.check_title("About")
        self.check_h1("About")

        # There is some helpful text
        box = self.browser.find_element_by_class_name("about-box")
        self.assertGreaterEqual(len(box.find_elements_by_tag_name("p")), 3)



class ChangelogPageTests(FunctionalTest):

    def test_changelog_page_layout(self):
        # They go to the changelog page
        self.get("/")
        footer = self.browser.find_element_by_tag_name("footer")
        self.click(footer.find_element_by_link_text("Changelog"))
        self.check_title("Changelog")
        self.check_h1("Changelog")

        # There are multiple releases
        self.assertGreaterEqual(
         len(self.browser.find_elements_by_class_name("release")), 3
        )



class HelpPageTests(FunctionalTest):

    def test_help_page_layout(self):
        # They go to the help page
        self.get("/")
        nav = self.browser.find_element_by_tag_name("nav")
        nav_links = nav.find_element_by_id("nav-links")
        self.click(nav_links.find_element_by_link_text("Help"))
        self.check_title("Help")
        self.check_h1("How to use")

        # There are multiple help scenarios
        self.assertGreaterEqual(
         len(self.browser.find_elements_by_class_name("about-box")), 3
        )
