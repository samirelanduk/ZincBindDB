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
        self.input_site("", "A247", "A57", "A97", "A99")

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


    def test_missing_zinc(self):
        self.login()

        # They enter a zinc binding site and submit
        self.input_site("1TON", "", "A57", "A97", "A99")

        # They are still on the same page
        self.check_page("/sites/new/")

        # There is an error message
        error = self.browser.find_element_by_class_name("error-message")
        self.assertIn("no zinc", error.text.lower())


    def test_cannot_create_same_site_in_pdb(self):
        self.login()

        # They enter a zinc binding site and submit
        self.input_site("5O8H", "A501", "A38", "A62", "A153")

        # They are still on the same page
        self.check_page("/sites/new/")

        # There is an error message
        error = self.browser.find_element_by_class_name("error-message")
        self.assertIn("already", error.text.lower())


    def test_cannot_create_zinc_site_with_zinc_that_doesnt_exist(self):
        self.login()

        # They enter a zinc binding site and submit
        self.input_site("1TON", "A1111", "A38", "A62", "A153")

        # They are still on the same page
        self.check_page("/sites/new/")

        # There is an error message
        error = self.browser.find_element_by_class_name("error-message")
        self.assertIn("there is no zinc", error.text.lower())


    def test_missing_residues(self):
        self.login()

        # They enter a zinc binding site and submit
        self.input_site("1TON", "A247", "", "", "")

        # They are still on the same page
        self.check_page("/sites/new/")

        # There is an error message
        error = self.browser.find_element_by_class_name("error-message")
        self.assertIn("no residue", error.text.lower())


    def test_some_missing_residues(self):
        self.login()

        # They enter a zinc binding site and submit
        self.input_site("1TON", "A247", "A57", "", "A99")

        # They are on the page for the new site
        self.check_page("/sites/1TONA247/")
        self.check_title("Site 1TONA247")
        self.check_h1("Zinc Site: 1TONA247")

        # The new site looks fine
        self.check_site_page(
         "1TON", "3 June, 1987", "SUBMAXILLARY GLAND",
         ["A57", "A99"], ["HIS"] * 2
        )


    def test_can_create_zinc_site_from_existing_residues(self):
        self.login()

        # They enter a zinc binding site and submit
        self.input_site("5O8H", "A502", "A38", "A62", "A98")

        # They are on the page for the new site
        self.check_page("/sites/5O8HA502/")
        self.check_title("Site 5O8HA502")
        self.check_h1("Zinc Site: 5O8HA502")

        # The new site looks fine
        self.check_site_page(
         "5O8H", "11 October, 2017", "CRYSTAL STRUCTURE OF R. RUBER",
         ["A38", "A62", "A98"], ["CYS", "HIS", "CYS"]
        )


    def test_cannot_create_zinc_site_with_residues_that_doesnt_exist(self):
        self.login()

        # They enter a zinc binding site and submit
        self.input_site("1TON", "A247", "A57", "A99999", "A99")

        # They are still on the same page
        self.check_page("/sites/new/")

        # There is an error message
        error = self.browser.find_element_by_class_name("error-message")
        self.assertIn("there is no residue", error.text.lower())
        self.assertIn("a99999", error.text.lower())



class SiteModificationTests(ManualSiteTest):

    def test_can_remove_residues(self):
        # User goes to site page, and there's no edit link
        self.get("/sites/5O8HA501/")
        edit_links = self.browser.find_elements_by_class_name("edit-link")
        self.assertFalse(edit_links)

        # They log in and there is an edit link, which they click
        self.login()
        self.get("/sites/5O8HA501/")
        edit_link = self.browser.find_element_by_class_name("edit-link")
        edit_link.find_element_by_tag_name("a").click()
        self.check_page("/sites/5O8HA501/edit/")
        self.check_title("Edit Zinc Site 5O8HA501")
        self.check_h1("Edit Zinc Site 5O8HA501")

        # There is a form there with values present for PDB and zinc ID
        site_form = self.browser.find_element_by_tag_name("form")
        pdb_input = site_form.find_elements_by_tag_name("input")[0]
        zinc_input = site_form.find_elements_by_tag_name("input")[1]
        self.assertEqual(pdb_input.get_attribute("value"), "5O8H")
        self.assertEqual(zinc_input.get_attribute("value"), "A501")
        self.assertFalse(pdb_input.is_enabled())
        self.assertFalse(zinc_input.is_enabled())
