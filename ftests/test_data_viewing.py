from .base import FunctionalTest

class PdbPageTests(FunctionalTest):

    def test_pdb_page_layout(self):
        # User goes to PDB page
        self.get("/pdbs/A001/")
        self.check_title("A001")
        self.check_h1("A001")
