from time import sleep
from .base import FunctionalTest

class SiteCreationTests(FunctionalTest):

    def test_can_create_new_site(self):
        self.login()

        # There is a nav link to the creation page
        nav_links = self.browser.find_element_by_id("nav-links")
        nav_links = nav_links.find_elements_by_tag_name("a")
        self.assertEqual(nav_links[-2].text, "New Site")

        # They click it
        nav_links[-2].click()
        self.check_page("/sites/new/")
        self.check_title("New Zinc Site")
        self.check_h1("New Zinc Site")

        # They enter a zinc binding site and submit
        self.input_site("1TON", "A247", "A57", "A97", "A99")

        # They are on the page for the new site
        self.check_page("/sites/1TONA247/")
        self.check_title("Site 1TONA247")
        self.check_h1("Zinc Site: 1TONA247")

        # The new site looks fine
        self.check_site_page(
         "1TON", "3 June, 1987", "SUBMAXILLARY GLAND",
         ["A57", "A97", "A99"], ["HIS"] * 3
        )
