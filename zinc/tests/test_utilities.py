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



class SkeletonPdbTests(DjangoTest):

    def setUp(self):
        self.model = Mock()
        self.atoms = [Mock() for _ in range(5)]
        for a, n in zip(self.atoms, ["N", "CA", "C", "O", "CB"]): a.name = n
        chaina, chainb = Mock(), Mock()
        chaina.atoms.return_value = set(self.atoms[:3])
        chainb.atoms.return_value = set(self.atoms[3:])
        self.model.chains.return_value = set([chaina, chainb])


    def test_can_pass_model(self):
        self.assertFalse(model_is_skeleton(self.model))


    def test_can_fail_model(self):
        self.atoms[4].name = "CA"
        self.assertTrue(model_is_skeleton(self.model))
