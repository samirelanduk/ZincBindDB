from time import sleep
from .base import BrowserTest

class SiteTests(BrowserTest):

    def test_can_view_zinc_site(self):
        self.get("/1AADA200/")
        self.check_title("1AADA200")
        self.check_h1("Zinc Site: 1AADA200")

        # There is a PDB section
        pdb_section = self.browser.find_element_by_id("site-pdb")
        pdb_title = pdb_section.find_element_by_tag_name("h2")
        self.assertIn("PDB", pdb_title.text)
        table = pdb_section.find_element_by_tag_name("table")
        self.check_table_values(table, [
         ["PDB Code", "1AAD"], ["Deposition Date", "4 January, 2012"],
         ["Title", "PDB 4"], ["Technique", "NMR"],
         ["Resolution", "4.7"], ["Rfactor", "9.4"],
         ["Classification", "LYASE"], ["Source Organism", "Homo sapiens"],
         ["Expression System", "E. coli"]
        ])

        # There is a residues section
        residues_section = self.browser.find_element_by_id("site-residues")
        residues_title = residues_section.find_element_by_tag_name("h2")
        self.assertIn("Residues", residues_section.text)

        # There are residue divs
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
             rows[1].find_elements_by_tag_name("td")[1].text, "A1" + str(index + 1)
            )
            self.assertEqual(
             rows[2].find_elements_by_tag_name("td")[1].text, "CYS" if index % 2 else "VAL"
            )
