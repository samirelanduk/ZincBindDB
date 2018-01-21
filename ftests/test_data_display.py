from time import sleep
from zincbind.models import ZincSite, Pdb
from .base import BrowserTest

class SiteTests(BrowserTest):

    def test_can_view_zinc_site(self):
        pdb = Pdb.objects.get(id="A081")
        pdb.classification = "XXX"
        pdb.save()
        self.get("/A081A0/")
        self.check_title("A081A0")
        self.check_h1("Zinc Site: A081A0")

        # There is a site section
        site_section = self.browser.find_element_by_id("site")

        # It has two panels
        panels = site_section.find_elements_by_class_name("half-width")
        self.assertEqual(len(panels), 2)

        # The first panel has the ngl display
        ngl_container = panels[0].find_element_by_id("ngl-container")
        ngl_header = ngl_container.find_element_by_class_name("box-header")
        self.assertIn("3D", ngl_header.text)
        ngl = ngl_container.find_element_by_id("ngl-site")
        ngl_bottom = panels[0].find_element_by_class_name("box-legend")
        self.assertIn("click", ngl_bottom.text.lower())

        # There is also a GUI selector in the first panel
        gui = panels[0].find_element_by_class_name("gui-selector")
        select = panels[0].find_element_by_tag_name("select")
        gui_text = panels[0].find_element_by_tag_name("code")
        self.assertEqual(gui_text.text, "")
        self.select_dropdown(select, "PyMol")
        self.assertIn("sele ", gui_text.text)
        self.select_dropdown(select, "VMD")
        self.assertIn("resid ", gui_text.text)
        self.select_dropdown(select, "")
        self.assertEqual(gui_text.text, "")

        # The second panel has the residue information
        residues = panels[1].find_element_by_class_name("site-residues")
        residues = residues.find_elements_by_class_name("residue")
        self.assertEqual(len(residues), 3)
        self.assertIn("Valine (A11)", residues[0].text)
        self.assertIn("CA distance: 2.18 Å", residues[0].text)
        self.assertIn("CB distance: 0.87 Å", residues[0].text)
        self.assertIn("Cysteine (A12)", residues[1].text)
        self.assertIn("CA distance: 2.18 Å", residues[1].text)
        self.assertIn("CB distance: 0.87 Å", residues[1].text)
        self.assertIn("Valine (A13)", residues[2].text)
        self.assertIn("CA distance: 2.18 Å", residues[2].text)
        self.assertIn("CB distance: 0.87 Å", residues[2].text)

        # The second panel also has the hydrophobicity chart
        chart = panels[1].find_element_by_id("solvation-chart")

        # There is a PDB section
        pdb_section = self.browser.find_element_by_id("site-pdb")
        table = pdb_section.find_element_by_tag_name("table")
        self.check_table_values(table, [
         ["PDB Code", "A081"], ["Deposition Date", "2 January, 2012"],
         ["Title", "PDB 1"], ["Technique", "X-RAY"],
         ["Resolution", "5.0"], ["Rfactor", "10.0"],
         ["Classification", "XXX"], ["Source Organism", "Mus musculus"],
         ["Expression System", "E. coli"]
        ])

        # There is a list of other sites in this PDB - there aren't any
        other_in_pdb = pdb_section.find_elements_by_tag_name("table")[1]
        self.assertIn("PDB", other_in_pdb.find_element_by_tag_name("th").text)
        rows = other_in_pdb.find_elements_by_tag_name("tr")
        self.assertEqual(len(rows), 2)
        self.assertIn("None", rows[1].text)

        # There is a list of other sites in this class - there aren't any
        other_in_class = pdb_section.find_elements_by_tag_name("table")[2]
        self.assertIn(
         "Class", other_in_class.find_element_by_tag_name("th").text
        )
        rows = other_in_class.find_elements_by_tag_name("tr")
        self.assertEqual(len(rows), 2)
        self.assertIn("None", rows[1].text)


    def test_can_get_links_to_other_sites(self):
        self.get("/A082A100/")
        pdb_section = self.browser.find_element_by_id("site-pdb")

        # There is a list of other sites in this PDB - there is one
        other_in_pdb = pdb_section.find_elements_by_tag_name("table")[1]
        rows = other_in_pdb.find_elements_by_tag_name("tr")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1].text, "A082B100")

        # There is a list of other sites in this class - there are two
        other_in_class = pdb_section.find_elements_by_tag_name("table")[2]
        self.assertIn(
         "Class", other_in_class.find_element_by_tag_name("th").text
        )
        rows = other_in_class.find_elements_by_tag_name("tr")
        self.assertEqual(len(rows), 4)
        self.assertIn("A082B100", other_in_class.text)
        self.assertIn("A091A1000", other_in_class.text)
        self.assertIn("A100A1900", other_in_class.text)

        # The links work
        first = rows[1].text.split()[0]
        self.click(rows[1].find_element_by_tag_name("a"))
        self.check_page("/{}/".format(first))
        self.browser.back()
        pdb_section = self.browser.find_element_by_id("site-pdb")
        other_in_pdb = pdb_section.find_elements_by_tag_name("table")[1]
        rows = other_in_pdb.find_elements_by_tag_name("tr")
        first = rows[1].text.split()[0]
        self.click(rows[-1].find_element_by_tag_name("a"))
        sleep(0.4)
        self.check_page("/{}/".format(first))


    def test_can_get_many_links_to_other_sites(self):
        pdb = Pdb.objects.get(id="A082")
        pdb.classification = "LYASE"
        pdb.save()
        ZincSite.objects.create(
         id="A082A1023", x=1.5, y=2.5, z=2.5, pdb=pdb
        )
        ZincSite.objects.create(
         id="A082A1024", x=1.5, y=2.5, z=2.5, pdb=pdb
        )
        ZincSite.objects.create(
         id="A082A1025", x=1.5, y=2.5, z=2.5, pdb=pdb
        )
        ZincSite.objects.create(
         id="A082A1026", x=1.5, y=2.5, z=2.5, pdb=pdb
        )
        self.get("/A082A100/")
        pdb_section = self.browser.find_element_by_id("site-pdb")

        # There is a list of other sites in this PDB - there are many
        other_in_pdb = pdb_section.find_elements_by_tag_name("table")[1]
        rows = other_in_pdb.find_elements_by_tag_name("tr")
        self.assertEqual(len(rows), 4)
        self.assertIn("See all 6", rows[3].text)

        # There is a list of other sites in this class - there are two
        other_in_class = pdb_section.find_elements_by_tag_name("table")[2]
        rows = other_in_class.find_elements_by_tag_name("tr")
        self.assertEqual(len(rows), 4)
        self.assertIn("See all 26", rows[3].text)

        self.click(rows[-1].find_element_by_tag_name("a"))
        sleep(0.4)
        self.check_page("/search?classification=LYASE")
        self.browser.back()
        pdb_section = self.browser.find_element_by_id("site-pdb")
        other_in_pdb = pdb_section.find_elements_by_tag_name("table")[1]
        rows = other_in_pdb.find_elements_by_tag_name("tr")
        self.click(rows[-1].find_element_by_tag_name("a"))
        sleep(0.4)
        self.check_page("/search?code=A082")


    def test_can_handle_classification_being_none(self):
        pdb = Pdb.objects.get(id="A082")
        pdb.classification = None
        pdb.save()
        self.get("/A082A100/")
        pdb_section = self.browser.find_element_by_id("site-pdb")

        # There is a list of other sites in this class - there aren't any
        pdb_section = self.browser.find_element_by_id("site-pdb")
        other_in_class = pdb_section.find_elements_by_tag_name("table")[2]
        rows = other_in_class.find_elements_by_tag_name("tr")
        self.assertEqual(len(rows), 2)
        self.assertIn("None", rows[1].text)
