from unittest.mock import patch, Mock, MagicMock
from .base import FunctionalTest
from zincbind.models import *
from scripts.add_pdbs import main

class AddingScriptTests(FunctionalTest):

    @patch("scripts.add_pdbs.get_all_pdb_codes")
    @patch("builtins.print")
    def test_can_check_empty_pdbs(self, mock_print, mock_get):
        self.assertEqual(len(Pdb.objects.all()), 8)
        self.assertEqual(len(ZincSite.objects.all()), 4)
        self.assertEqual(len(Residue.objects.all()), 12)
        self.assertEqual(len(Atom.objects.all()), 48)
        mock_get.return_value = [
         "1AAA", "1AAB", "1AAC", "1AAD", "2AAA", "2AAB", "2AAC", "2AAD",
         "1LOL", "2SAM"
        ]
        main()
        mock_print.assert_any_call("There are 10 current PDB codes.")
        mock_print.assert_any_call("There are 2 which have never been checked.")
        for code in mock_get.return_value:
            mock_print.assert_any_call("\tChecking {}...".format(code))
        self.assertEqual(len(Pdb.objects.all()), 10)
        self.assertEqual(len(ZincSite.objects.all()), 4)
        self.assertEqual(len(Residue.objects.all()), 12)
        self.assertEqual(len(Atom.objects.all()), 48)


    @patch("scripts.add_pdbs.get_all_pdb_codes")
    @patch("builtins.print")
    def test_can_ignore_skeleton_pdbs(self, mock_print, mock_get):
        self.assertEqual(len(Pdb.objects.all()), 8)
        self.assertEqual(len(ZincSite.objects.all()), 4)
        self.assertEqual(len(Residue.objects.all()), 12)
        self.assertEqual(len(Atom.objects.all()), 48)
        mock_get.return_value = [
         "1AAA", "1AAB", "1AAC", "1AAD", "2AAA", "2AAB", "2AAC", "2AAD",
         "1LOL", "2SAM", "1A1Q"
        ]
        main()
        mock_print.assert_any_call("There are 11 current PDB codes.")
        mock_print.assert_any_call("There are 3 which have never been checked.")
        for code in mock_get.return_value:
            mock_print.assert_any_call("\tChecking {}...".format(code))
        mock_print.assert_any_call("\tDiscounting 1A1Q - skeleton PDB")
        self.assertEqual(len(Pdb.objects.all()), 11)
        self.assertEqual(len(ZincSite.objects.all()), 4)
        self.assertEqual(len(Residue.objects.all()), 12)
        self.assertEqual(len(Atom.objects.all()), 48)


    @patch("scripts.add_pdbs.get_all_pdb_codes")
    @patch("builtins.print")
    def test_successful_add(self, mock_print, mock_get):
        self.assertEqual(len(Pdb.objects.all()), 8)
        self.assertEqual(len(ZincSite.objects.all()), 4)
        self.assertEqual(len(Residue.objects.all()), 12)
        self.assertEqual(len(Atom.objects.all()), 48)
        mock_get.return_value = [
         "1AAA", "1AAB", "1AAC", "1AAD", "2AAA", "2AAB", "2AAC", "2AAD",
         "1LOL", "2SAM", "1A1Q", "1TON"
        ]
        main()
        mock_print.assert_any_call("There are 12 current PDB codes.")
        mock_print.assert_any_call("There are 4 which have never been checked.")
        for code in mock_get.return_value:
            mock_print.assert_any_call("\tChecking {}...".format(code))
        mock_print.assert_any_call("\t\tAdded <'A247' Site (3 residues)>")
        self.assertEqual(len(Pdb.objects.all()), 12)
        self.assertEqual(len(ZincSite.objects.all()), 5)
        self.assertEqual(len(Residue.objects.all()), 15)
        self.assertEqual(len(Atom.objects.all()), 78)


    @patch("scripts.add_pdbs.get_all_pdb_codes")
    @patch("builtins.print")
    def test_filtering_of_zero_residue_sites(self, mock_print, mock_get):
        self.assertEqual(len(Pdb.objects.all()), 8)
        self.assertEqual(len(ZincSite.objects.all()), 4)
        self.assertEqual(len(Residue.objects.all()), 12)
        self.assertEqual(len(Atom.objects.all()), 48)
        mock_get.return_value = [
         "1AAA", "1AAB", "1AAC", "1AAD", "2AAA", "2AAB", "2AAC", "2AAD",
         "1LOL", "2SAM", "1A1Q", "1TON", "1W25"
        ]
        main()
        mock_print.assert_any_call("There are 13 current PDB codes.")
        mock_print.assert_any_call("There are 5 which have never been checked.")
        for code in mock_get.return_value:
            mock_print.assert_any_call("\tChecking {}...".format(code))
        mock_print.assert_any_call("\t\tAdded <'A247' Site (3 residues)>")
        mock_print.assert_any_call("\t\tNot adding <'A499' Site (0 residues)>")
        self.assertEqual(len(Pdb.objects.all()), 12)
        self.assertEqual(len(ZincSite.objects.all()), 5)
        self.assertEqual(len(Residue.objects.all()), 15)
        self.assertEqual(len(Atom.objects.all()), 78)


    @patch("scripts.add_pdbs.get_all_pdb_codes")
    @patch("builtins.print")
    def test_water_residues(self, mock_print, mock_get):
        self.assertEqual(len(Pdb.objects.all()), 8)
        self.assertEqual(len(ZincSite.objects.all()), 4)
        self.assertEqual(len(Residue.objects.all()), 12)
        self.assertEqual(len(Atom.objects.all()), 48)
        mock_get.return_value = [
         "1AAA", "1AAB", "1AAC", "1AAD", "2AAA", "2AAB", "2AAC", "2AAD",
         "1LOL", "2SAM", "1A1Q", "1TON", "1W25", "12CA"
        ]
        main()
        mock_print.assert_any_call("There are 14 current PDB codes.")
        mock_print.assert_any_call("There are 6 which have never been checked.")
        for code in mock_get.return_value:
            mock_print.assert_any_call("\tChecking {}...".format(code))
        mock_print.assert_any_call("\t\tAdded <'A247' Site (3 residues)>")
        mock_print.assert_any_call("\t\tAdded <'A262' Site (6 residues)>")
        mock_print.assert_any_call("\t\tNot adding <'A499' Site (0 residues)>")
        self.assertEqual(len(Pdb.objects.all()), 13)
        self.assertEqual(len(ZincSite.objects.all()), 6)
        self.assertEqual(len(Residue.objects.all()), 21)
        self.assertEqual(len(Atom.objects.all()), 125)


    @patch("scripts.add_pdbs.get_all_pdb_codes")
    @patch("builtins.print")
    def test_rcsb_problems(self, mock_print, mock_get):
        self.assertEqual(len(Pdb.objects.all()), 8)
        self.assertEqual(len(ZincSite.objects.all()), 4)
        self.assertEqual(len(Residue.objects.all()), 12)
        self.assertEqual(len(Atom.objects.all()), 48)
        mock_get.return_value = [
         "1AAA", "1AAB", "1AAC", "1AAD", "2AAA", "2AAB", "2AAC", "2AAD",
         "1LOL", "2SAM", "1A1Q", "1TON", "1W25", "12CA", "4V6X"
        ]
        main()
        mock_print.assert_any_call("There are 15 current PDB codes.")
        mock_print.assert_any_call("There are 7 which have never been checked.")
        for code in mock_get.return_value:
            mock_print.assert_any_call("\tChecking {}...".format(code))
        mock_print.assert_any_call("\t\tAdded <'A247' Site (3 residues)>")
        mock_print.assert_any_call("\t\tAdded <'A262' Site (6 residues)>")
        mock_print.assert_any_call("\t\tNot adding <'A499' Site (0 residues)>")
        mock_print.assert_any_call("\tCould not obtain 4V6X from RCSB")
        self.assertEqual(len(Pdb.objects.all()), 13)
        self.assertEqual(len(ZincSite.objects.all()), 6)
        self.assertEqual(len(Residue.objects.all()), 21)
        self.assertEqual(len(Atom.objects.all()), 125)


    @patch("scripts.add_pdbs.get_all_pdb_codes")
    @patch("builtins.print")
    @patch("zincbind.factories.Atom.objects.create")
    def test_transactions_work(self, mock_create, mock_print, mock_get):
        self.assertEqual(len(Pdb.objects.all()), 8)
        self.assertEqual(len(ZincSite.objects.all()), 4)
        self.assertEqual(len(Residue.objects.all()), 12)
        self.assertEqual(len(Atom.objects.all()), 48)
        mock_get.return_value = [
         "1AAA", "1AAB", "1AAC", "1AAD", "2AAA", "2AAB", "2AAC", "2AAD",
         "1TON"
        ]
        mock_create.side_effect = KeyboardInterrupt
        try:
            main()
        except: pass
        mock_print.assert_any_call("There are 9 current PDB codes.")
        mock_print.assert_any_call("There are 1 which have never been checked.")
        for code in mock_get.return_value:
            mock_print.assert_any_call("\tChecking {}...".format(code))
        self.assertEqual(len(Pdb.objects.all()), 8)
        self.assertEqual(len(ZincSite.objects.all()), 4)
        self.assertEqual(len(Residue.objects.all()), 12)
        self.assertEqual(len(Atom.objects.all()), 48)
