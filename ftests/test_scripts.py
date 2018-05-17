from unittest.mock import patch, Mock, MagicMock
from testarsenal import DjangoTest
from zinc.models import *
from scripts.build_db import main

class DatabaseBuildingTests(DjangoTest):

    def setUp(self):
        self.patch1 = patch("scripts.build_db.get_zinc_pdb_codes")
        self.patch2 = patch("builtins.print")
        self.patch3 = patch("scripts.build_db.tqdm")
        self.mock_codes = self.patch1.start()
        self.mock_print = self.patch2.start()
        self.mock_tqdm = self.patch3.start()
        self.mock_tqdm.side_effect = lambda l: l
        self.skeletons = ["1A1Q", "4UXY"]
        self.standard = ["1TON", "6EQU"]



    def tearDown(self):
        self.patch1.stop()
        self.patch2.stop()
        self.patch3.stop()


    def check_print_statement(self, fragment):
        for call in self.mock_print.call_args_list:
            if fragment in call[0][0]: break
        else:
            raise ValueError(f"No print call with '{fragment}' in")


    def test_script(self):
        self.mock_codes.return_value = self.standard
        main()
        self.check_print_statement("2 PDBs with zinc")
        self.assertEqual(Pdb.objects.count(), 2)
        self.assertFalse(Pdb.objects.get(id="1TON").skeleton)
        self.assertFalse(Pdb.objects.get(id="6EQU").skeleton)
        self.assertTrue(
         Pdb.objects.get(id="1TON").title.startswith("RAT SUBMAXILLARY GLAND")
        )
        self.assertEqual(Chain.objects.count(), 2)
        chain1 = Chain.objects.get(id="1TONA")
        self.assertEqual(chain1.sequence[:10], "IVGGYKCEKN")
        self.assertEqual(Zinc.objects.count(), 2)
        zinc1 = Zinc.objects.get(id="6EQU2134")
        self.assertEqual(zinc1.x, -6.582)
