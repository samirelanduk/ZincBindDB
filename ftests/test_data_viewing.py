from .base import FunctionalTest

class PdbPageTests(FunctionalTest):

    def test_pdb_page_layout(self):
        # User goes to PDB page
        self.get("/pdbs/A001/")
        self.check_title("A001")
        self.check_h1("A SUPERB PDB FILE")

        # There is information about the PDB
        pdb_information = self.browser.find_element_by_id("pdb-info")
        self.assertIn("Deposition Date: 28 September, 1990", pdb_information.text)
        self.assertIn("Classification: REDUCTASE", pdb_information.text)
        self.assertIn("Technique: X-RAY", pdb_information.text)
        self.assertIn("Source Organism: Felis catus", pdb_information.text)
        self.assertIn("Expression System: Escherichia coli BL21(DE3)", pdb_information.text)
        self.assertIn("Resolution: 2.1 Å", pdb_information.text)
        self.assertIn("R-factor: 4.5 Å", pdb_information.text)
        self.assertIn("Code: A001", pdb_information.text)
