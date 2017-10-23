from time import sleep
from .base import FunctionalTest

class ManualSiteTest(FunctionalTest):

    def setUp(self):
        FunctionalTest.setUp(self)


    def input_site(self, pdb, zincid, res1, res2, res3):
        # There is a nav link to the creation page
        self.get("/")
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
        pdb_input.send_keys(pdb)

        # They enter the zinc ID
        zinc_input = site_form.find_elements_by_tag_name("input")[1]
        zinc_input.send_keys(zincid)

        # They enter the residues
        residue_input_div = site_form.find_element_by_id("residue-inputs")
        inputs = residue_input_div.find_elements_by_tag_name("input")
        self.assertEqual(len(inputs), 1)
        inputs[0].send_keys(res1)
        buttons = residue_input_div.find_elements_by_tag_name("button")
        self.assertEqual(len(buttons), 2)
        self.click(buttons[-1])
        inputs = residue_input_div.find_elements_by_tag_name("input")
        self.assertEqual(len(inputs), 2)
        inputs[1].send_keys(res2)
        buttons = residue_input_div.find_elements_by_tag_name("button")
        self.assertEqual(len(buttons), 3)
        self.browser.execute_script(
         "window.scrollTo(0, document.body.scrollHeight);"
        )
        self.click(buttons[-1])
        inputs = residue_input_div.find_elements_by_tag_name("input")
        self.assertEqual(len(inputs), 3)
        inputs[2].send_keys("WRONG")
        buttons = residue_input_div.find_elements_by_tag_name("button")
        self.assertEqual(len(buttons), 4)
        self.click(buttons[-1])
        inputs = residue_input_div.find_elements_by_tag_name("input")
        self.assertEqual(len(inputs), 4)
        inputs[3].send_keys(res3)
        buttons = residue_input_div.find_elements_by_tag_name("button")
        self.assertEqual(len(buttons), 5)
        self.click(buttons[-3])
        inputs = residue_input_div.find_elements_by_tag_name("input")
        self.assertEqual(len(inputs), 3)
        buttons = residue_input_div.find_elements_by_tag_name("button")
        self.assertEqual(len(buttons), 4)

        # They submit the site
        submit_button = zinc_input = site_form.find_elements_by_tag_name("input")[-1]
        self.click(submit_button)



class SiteCreationTests(ManualSiteTest):

    def test_can_create_new_site(self):
        self.login()

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


    def test_can_create_site_in_existing_pdb(self):
        self.login()

        # They enter a zinc binding site and submit
        self.input_site("5O8H", "A502", "A38", "A62", "A153")

        # They are on the page for the new site
        self.check_page("/sites/5O8HA502/")
        self.check_title("Site 5O8HA502")
        self.check_h1("Zinc Site: 5O8HA502")

        # The new site looks fine
        self.check_site_page(
         "5O8H", "11 October, 2017", "CRYSTAL STRUCTURE OF R. RUBER",
         ["A38", "A62", "A153"], ["CYS", "HIS", "ASP"]
        )


    def test_missing_pdb(self):
        self.login()

        # They enter a zinc binding site and submit
        self.input_site("", "A502", "A38", "A62", "A153")

        # They are still on the same page
        self.check_page("/sites/new/")

        # There is an error message
        error = self.browser.find_element_by_class_name("error-message")
        self.assertIn("no pdb", error.text.lower())


    def test_invalid_pdb(self):
        self.login()

        # They enter a zinc binding site and submit
        self.input_site("XXXX", "A502", "A38", "A62", "A153")

        # They are still on the same page
        self.check_page("/sites/new/")

        # There is an error message
        error = self.browser.find_element_by_class_name("error-message")
        self.assertIn("valid pdb", error.text.lower())

        # They try again
        self.input_site("gweauyfeuyf", "A502", "A38", "A62", "A153")

        # They are still on the same page
        self.check_page("/sites/new/")

        # There is an error message
        error = self.browser.find_element_by_class_name("error-message")
        self.assertIn("valid pdb", error.text.lower())


    def test_cannot_create_same_site_in_pdb(self):
        self.login()

        # There is a nav link to the creation page
        nav_links = self.browser.find_element_by_id("nav-links")
        nav_links = nav_links.find_elements_by_tag_name("a")
        self.assertEqual(nav_links[-2].text, "New Site")
        nav_links[-2].click()

        # They enter a zinc binding site and submit
        self.input_site("5O8H", "A501", "A38", "A62", "A153")

        # They are still on the same page
        self.check_page("/sites/new/")

        # There is an error message
        error = self.browser.find_element_by_class_name("error-message")
        self.assertIn("already", error.text.lower())


    def test_cannot_create_zinc_site_with_zinc_that_doesnt_exist(self):
        self.login()

        # There is a nav link to the creation page
        nav_links = self.browser.find_element_by_id("nav-links")
        nav_links = nav_links.find_elements_by_tag_name("a")
        self.assertEqual(nav_links[-2].text, "New Site")
        nav_links[-2].click()

        # They enter a zinc binding site and submit
        self.input_site("5O8H", "A1111", "A38", "A62", "A153")

        # They are still on the same page
        self.check_page("/sites/new/")

        # There is an error message
        error = self.browser.find_element_by_class_name("error-message")
        self.assertIn("there is no zinc", error.text.lower())
