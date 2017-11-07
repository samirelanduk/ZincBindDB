from unittest.mock import patch
from .base import FunctionalTest
from zincbind.models import *
from scripts.add_pdbs import main

class AddingScriptTests(FunctionalTest):

    @patch("scripts.add_pdbs.get_all_pdb_codes")
    @patch("builtins.print")
    def test_successful_add(self, mock_print, mock_add):
        from pprint import pprint
        pprint("test_script")
        self.assertEqual(len(Pdb.objects.all()), 8)
        self.assertEqual(len(ZincSite.objects.all()), 4)
        self.assertEqual(len(Residue.objects.all()), 12)
        self.assertEqual(len(Atom.objects.all()), 48)
        mock_add.return_value = [
         "1AAA", "1AAB", "1AAC", "1AAD", "2AAA", "2AAB", "2AAC", "2AAD",
         "2SAM", "1LOL", "1TON"
        ]
        main()
        mock_print.assert_any_call("There are 11 current PDB codes.")
        mock_print.assert_any_call("There are 3 which have never been checked.")
        for code in mock_add.return_value:
            mock_print.assert_any_call("\tChecking {}...".format(code))
        mock_print.assert_any_call("\t\tAdded <'A247' Site (3 residues)>")
        self.assertEqual(len(Pdb.objects.all()), 11)
        self.assertEqual(len(ZincSite.objects.all()), 5)
        self.assertEqual(len(Residue.objects.all()), 15)
        self.assertEqual(len(Atom.objects.all()), 78)
