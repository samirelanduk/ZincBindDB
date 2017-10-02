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
        self.browser.execute_script(
         "window.scrollTo(0, document.body.scrollHeight);"
        )
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

        # There is a PDB section
        pdb_section = self.browser.find_element_by_id("site-pdb")
        pdb_title = pdb_section.find_element_by_tag_name("h2")
        self.assertIn("PDB", pdb_title.text)
        table = pdb_section.find_element_by_tag_name("table")
        rows = table.find_elements_by_tag_name("tr")
        self.assertEqual(
         rows[0].find_elements_by_tag_name("td")[0].text, "PDB Code"
        )
        self.assertEqual(
         rows[1].find_elements_by_tag_name("td")[0].text, "Deposition Date"
        )
        self.assertEqual(
         rows[2].find_elements_by_tag_name("td")[0].text, "Title"
        )
        self.assertEqual(
         rows[0].find_elements_by_tag_name("td")[1].text, "1TON"
        )
        self.assertEqual(
         rows[1].find_elements_by_tag_name("td")[1].text, "3 June, 1987"
        )
        self.assertIn(
         "SUBMAXILLARY GLAND", rows[2].find_elements_by_tag_name("td")[1].text,
        )

        # There is a residues section
        residues_section = self.browser.find_element_by_id("site-residues")
        residues_title = residues_section.find_element_by_tag_name("h2")
        self.assertIn("Residues", residues_section.text)

        # There are three residue divs
        residue_divs = self.browser.find_elements_by_class_name("residue")
        self.assertEqual(len(residue_divs), 3)

        # The residue divs are correct
        for index, residue_div in enumerate(residue_divs):
            table = residue_div.find_element_by_tag_name("table")
            rows = table.find_elements_by_tag_name("tr")
            self.assertEqual(
             rows[0].find_elements_by_tag_name("td")[0].text, "Chain"
            )
            self.assertEqual(
             rows[1].find_elements_by_tag_name("td")[0].text, "ID"
            )
            self.assertEqual(
             rows[2].find_elements_by_tag_name("td")[0].text, "Name"
            )
            self.assertEqual(
             rows[0].find_elements_by_tag_name("td")[1].text, "A"
            )
            self.assertEqual(
             rows[1].find_elements_by_tag_name("td")[1].text, ["A57", "A97", "A99"][index]
            )
            self.assertEqual(
             rows[2].find_elements_by_tag_name("td")[1].text, "HIS"
            )
