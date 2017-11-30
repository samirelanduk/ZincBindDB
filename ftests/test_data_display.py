from time import sleep
from .base import BrowserTest

class SiteTests(BrowserTest):

    def test_can_view_zinc_site(self):
        self.get("/1AADA200/")
        self.check_title("1AADA200")
        self.check_h1("Zinc Site: 1AADA200")

        # There is a site section
        site_section = self.browser.find_element_by_id("site")

        # There are two panels
        panels = site_section.find_elements_by_class_name("half-width")
        self.assertEqual(len(panels), 2)

        # The first panel is an iframe
        iframe = panels[0].find_element_by_tag_name("iframe")
        self.assertEqual(
         iframe.get_attribute("src"), self.live_server_url + "/ngl/1AADA200/"
        )

        # The second panel has a table of data
        site_table = panels[1].find_element_by_tag_name("table")
        cells = [[cell.text for cell in row.find_elements_by_tag_name("td")]
         for row in site_table.find_elements_by_tag_name("tr")]
        self.assertEqual(cells[0][0], "Residues")
        self.assertIn("Valine (A11)", cells[0][1])
        self.assertIn("CA distance: 2.18 Å", cells[0][1])
        self.assertIn("CB distance: 0.87 Å", cells[0][1])
        self.assertIn("Cysteine (A12)", cells[0][1])
        self.assertIn("CA distance: 2.18 Å", cells[0][1])
        self.assertIn("CB distance: 0.87 Å", cells[0][1])
        self.assertIn("Valine (A13)", cells[0][1])
        self.assertIn("CA distance: 2.18 Å", cells[0][1])
        self.assertIn("CB distance: 0.87 Å", cells[0][1])
        self.assertEqual(cells[1][0], "PyMol Selector")
        self.assertEqual(cells[1][1], "sele 1AADA200, (chain A and resi 11) + (chain A and resi 12) + (chain A and resi 13) + (chain A and resi 200)")
        self.assertEqual(cells[2][0], "VMD Selector")
        self.assertEqual(cells[2][1], "(chain A and resid 11) or (chain A and resid 12) or (chain A and resid 13) or (chain A and resid 200)")

        # There is a PDB section
        pdb_section = self.browser.find_element_by_id("site-pdb")
        table = pdb_section.find_element_by_tag_name("table")
        self.check_table_values(table, [
         ["PDB Code", "1AAD"], ["Deposition Date", "4 January, 2012"],
         ["Title", "PDB 4"], ["Technique", "NMR"],
         ["Resolution", "4.7"], ["Rfactor", "9.4"],
         ["Classification", "LYASE"], ["Source Organism", "Homo sapiens"],
         ["Expression System", "E. coli"]
        ])
