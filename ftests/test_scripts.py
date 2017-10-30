from unittest.mock import patch
from .base import FunctionalTest
from zincbind.models import *
from scripts.add_pdbs import main

class AddingScriptTests(FunctionalTest):

    @patch("scripts.add_pdbs.get_all_pdb_codes")
    @patch("builtins.print")
    def test_successful_add(self, mock_print, mock_add):
        mock_add.return_value = [
         "1AAA", "1AAB", "1AAC", "1AAD", "2AAA", "2AAB", "2AAC", "2AAD",
         "2SAM", "1LOL", "1TON"
        ]
        main()
        self.assertEqual(len(Pdb.objects.all()), 11)
