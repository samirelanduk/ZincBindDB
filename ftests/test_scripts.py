from unittest.mock import patch, Mock, MagicMock
from testarsenal import DjangoTest
from zinc.models import *
from scripts.build_db import main

class DatabaseBuildingTests(DjangoTest):

    def setUp(self):
        self.patch1 = patch("scripts.build_db.get_zinc_pdb_codes")
        self.patch2 = patch("builtins.print")
        self.mock_codes = self.patch1.start()
        self.mock_print = self.patch2.start()
        self.skeletons = ["1A1Q", "4UXY"]


    def tearDown(self):
        self.patch1.stop()
        self.patch2.stop()


    def check_print_statement(self, fragment):
        for call in self.mock_print.call_args_list:
            if fragment in call[0][0]: break
        else:
            raise ValueError(f"No print call with '{fragment}' in")


    def test_script(self):
        self.mock_codes.return_value = self.skeletons
        main()
        self.check_print_statement("2 PDBs with zinc")
        self.assertEqual(Pdb.objects.count(), 2)
        self.assertTrue(Pdb.objects.get(id="1A1Q").skeleton)
        self.assertTrue(Pdb.objects.get(id="4UXY").skeleton)
        self.assertTrue(
         Pdb.objects.get(id="1A1Q").title, "HEPATITIS C VIRUS NS3 PROTEINASE"
        )
