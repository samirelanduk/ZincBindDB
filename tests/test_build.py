import sys
sys.path.append("build")
from unittest.mock import patch, Mock, MagicMock
from django.test import LiveServerTestCase
from core.models import *
from build.build import main

class DatabaseBuildingTests(LiveServerTestCase):

    def setUp(self):
        self.patch1 = patch("build.build.get_zinc_pdb_codes")
        self.patch2 = patch("builtins.print")
        self.patch3 = patch("build.build.tqdm")
        self.mock_codes = self.patch1.start()
        self.mock_print = self.patch2.start()
        self.mock_tqdm = self.patch3.start()
        self.mock_tqdm.side_effect = lambda l: l


    def tearDown(self):
        self.patch1.stop()
        self.patch2.stop()
        self.patch3.stop()


    def check_print_statement(self, fragment):
        for call in self.mock_print.call_args_list:
            if fragment in call[0][0]: break
        else:
            raise ValueError(f"No print call with '{fragment}' in")


    def test_script_checking_only_new(self):
        Pdb.objects.create(id="1SP1", skeleton=False)
        self.mock_codes.return_value = ["1SP1", "3ZNF"]
        main()
        self.check_print_statement("There are 2 PDB codes with zinc")
        self.check_print_statement("1 of these need to be checked")


    def test_can_get_best_model(self):
        self.mock_codes.return_value = ["1B21"]
        main()
        pdb = Pdb.objects.get(id="1B21")
        self.assertIn("BURIED SALT BRIDGE", pdb.title)
        self.assertEqual(pdb.assembly, 3)


    def test_can_reject_skeleton_models(self):
        self.mock_codes.return_value = ["4UXY"]
        main()
        pdb = Pdb.objects.get(id="4UXY")
        self.assertIn("ATP binding", pdb.title)
        self.assertTrue(pdb.skeleton)
        self.assertEqual(pdb.metal_set.count(), 1)
        metal = pdb.metal_set.first()
        self.assertEqual(metal.atomium_id, 1171)
        self.assertEqual(metal.residue_number, 1413)
        self.assertEqual(metal.chain_id, "A")
        self.assertIn("no side chain", metal.omission_reason.lower())
