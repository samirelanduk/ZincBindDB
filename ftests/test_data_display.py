from time import sleep
from zincbind.models import ZincSite, Pdb
from .base import BrowserTest

class SiteTests(BrowserTest):

    def test_can_view_zinc_site(self):
        for i in range(2):
            ZincSite.objects.create(
             id="1AAD{}".format(i), x=1.5, y=2.5, z=2.5, pdb=Pdb.objects.get(id="1AAD")
            )
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

        # There is a list of other sites in this PDB
        other_in_pdb = pdb_section.find_elements_by_tag_name("table")[1]
        self.assertIn("PDB", other_in_pdb.find_element_by_tag_name("th").text)
        rows = other_in_pdb.find_elements_by_tag_name("tr")
        self.assertEqual(len(rows), 4)
        self.assertIn("1AADB200", other_in_pdb.text)
        self.assertIn("1AAD0", other_in_pdb.text)
        self.assertIn("1AAD1", other_in_pdb.text)

        # There is a list of other sites in this species
        other_in_species = pdb_section.find_elements_by_tag_name("table")[2]
        self.assertIn("Organism", other_in_species.find_element_by_tag_name("th").text)
        rows = other_in_species.find_elements_by_tag_name("tr")
        self.assertEqual(len(rows), 4)
        self.assertIn("1AADB200", other_in_species.text)
        self.assertIn("1AAD0", other_in_species.text)
        self.assertIn("1AAD1", other_in_species.text)

        # The links work
        first = rows[1].text.split()[0]
        self.click(rows[1].find_element_by_tag_name("a"))
        self.check_page("/{}/".format(first))


    def test_can_view_zinc_site_with_lots_of_matches(self):
        for i in range(20):
            ZincSite.objects.create(
             id="1AAD{}".format(i), x=1.5, y=2.5, z=2.5, pdb=Pdb.objects.get(id="1AAD")
            )
        self.get("/1AADA200/")
        self.check_title("1AADA200")
        self.check_h1("Zinc Site: 1AADA200")
        pdb_section = self.browser.find_element_by_id("site-pdb")

        # There is a list of other sites in this PDB
        other_in_pdb = pdb_section.find_elements_by_tag_name("table")[1]
        self.assertIn("PDB", other_in_pdb.find_element_by_tag_name("th").text)
        rows = other_in_pdb.find_elements_by_tag_name("tr")
        self.assertEqual(len(rows), 4)
        self.assertIn("1AADB200", other_in_pdb.text)
        self.assertIn("1AAD0", other_in_pdb.text)
        self.assertEqual(rows[-1].text, "See all 22 zinc sites in this PDB")

        # There is a list of other sites in this species
        other_in_species = pdb_section.find_elements_by_tag_name("table")[2]
        self.assertIn("Organism", other_in_species.find_element_by_tag_name("th").text)
        rows = other_in_species.find_elements_by_tag_name("tr")
        self.assertEqual(len(rows), 4)
        self.assertIn("1AADB200", other_in_species.text)
        self.assertIn("1AAD0", other_in_species.text)
        self.assertEqual(rows[-1].text, "See all 22 zinc sites in this Organism")

        # The links work
        self.click(rows[-1].find_element_by_tag_name("a"))
        sleep(0.4)
        self.check_page("/search?organism=HOMO%20SAPIENS")
        self.browser.back()
        pdb_section = self.browser.find_element_by_id("site-pdb")
        other_in_pdb = pdb_section.find_elements_by_tag_name("table")[1]
        rows = other_in_pdb.find_elements_by_tag_name("tr")
        self.click(rows[-1].find_element_by_tag_name("a"))
        sleep(0.4)
        self.check_page("/search?code=1AAD")
