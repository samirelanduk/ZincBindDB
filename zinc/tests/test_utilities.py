from unittest.mock import patch, Mock, MagicMock
from testarsenal import DjangoTest
from zinc.utilities import *

class ZincPdbTests(DjangoTest):

    @patch("requests.post")
    def test_can_get_all_zinc_pdbs(self, mock_post):
        response = Mock()
        response.status_code, response.text = 200, "1 2 3 " * 10000
        mock_post.return_value = response
        pdbs = get_zinc_pdb_codes()
        self.assertIn(b"formula>ZN</formula>", mock_post.call_args_list[0][1]["data"])
        self.assertEqual(pdbs, ["1", "2", "3"] * 10000)


    @patch("requests.post")
    def test_can_handle_request_going_wrong(self, mock_post):
        response = Mock()
        response.status_code, response.text = 500, "1 2 3 " * 10000
        mock_post.return_value = response
        with self.assertRaises(RcsbError):
            pdbs = get_zinc_pdb_codes()
        response.status_code, response.text = 200, "1 2 3"
        with self.assertRaises(RcsbError):
            pdbs = get_zinc_pdb_codes()
