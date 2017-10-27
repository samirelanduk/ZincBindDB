from unittest.mock import Mock, patch
from .base import ZincBindTest
from zincbind.utilities import *
from zincbind.exceptions import RcsbError

class PdbCodeGrabTests(ZincBindTest):

    @patch("requests.get")
    def test_can_get_all_pdb_codes(self, mock_get):
        response = Mock()
        response.status_code = 200
        response.text = ("<?xml version='1.0' standalone='no' ?>\n<current>\n  "
        "<PDB structureId=\"100D\" />\n  <PDB structureId=\"101D\" />\n  "
        "<PDB structureId=\"101M\" />\n</current>\n'")
        mock_get.return_value = response
        self.assertEqual(get_all_pdb_codes(), ["100D", "101D", "101M"])
        mock_get.assert_called_with("https://www.rcsb.org/pdb/rest/getCurrent")


    @patch("requests.get")
    def test_pdb_obtaining_can_throw_rcsb_error_on_500(self, mock_get):
        response = Mock()
        response.status_code = 500
        mock_get.return_value = response
        with self.assertRaises(RcsbError):
            get_all_pdb_codes()


    @patch("requests.get")
    def test_pdb_obtaining_can_throw_rcsb_error_when_unparsable(self, mock_get):
        response = Mock()
        response.status_code = 200
        response.text = "NONSENSE STRING"
        mock_get.return_value = response
        with self.assertRaises(RcsbError):
            get_all_pdb_codes()
