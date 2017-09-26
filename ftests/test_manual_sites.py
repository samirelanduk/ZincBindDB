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

        # There is a form
        site_form = self.browser.find_element_by_tag_name("form")

        # They enter the PDB code
        pdb_input = site_form.find_elements_by_tag_name("input")[0]
        pdb_input.send_keys("1TON")

        # They enter the zinc ID
        zinc_input = site_form.find_elements_by_tag_name("input")[1]
        zinc_input.send_keys("A247")

        # They enter the residues
        residue_input_div = site_form.find_element_by_id("residue-inputs")
        inputs = residue_input_div.find_elements_by_tag_name("input")
        self.assertEqual(len(inputs), 1)
        inputs[0].send_keys("A57")
        buttons = residue_input_div.find_elements_by_tag_name("button")
        self.assertEqual(len(buttons), 2)
        buttons[-1].click()
        inputs = residue_input_div.find_elements_by_tag_name("input")
        self.assertEqual(len(inputs), 2)
        inputs[1].send_keys("A97")
        buttons = residue_input_div.find_elements_by_tag_name("button")
        self.assertEqual(len(buttons), 3)
        buttons[-1].click()
        inputs = residue_input_div.find_elements_by_tag_name("input")
        self.assertEqual(len(inputs), 3)
        inputs[2].send_keys("WRONG")
        buttons = residue_input_div.find_elements_by_tag_name("button")
        self.assertEqual(len(buttons), 4)
        buttons[-1].click()
        inputs = residue_input_div.find_elements_by_tag_name("input")
        self.assertEqual(len(inputs), 4)
        inputs[3].send_keys("A99")
        buttons = residue_input_div.find_elements_by_tag_name("button")
        self.assertEqual(len(buttons), 5)
        buttons[-3].click()
        inputs = residue_input_div.find_elements_by_tag_name("input")
        self.assertEqual(len(inputs), 3)
        buttons = residue_input_div.find_elements_by_tag_name("button")
        self.assertEqual(len(buttons), 4)

        # They submit the site
        submit_button = zinc_input = site_form.find_elements_by_tag_name("input")[-1]
        submit_button.click()

        # They are on the page for the new site
        self.check_page("/sites/1TONA247/")
        self.check_title("Site 1TONA247")
        self.check_h1("Zinc Site: 1TONA247")
