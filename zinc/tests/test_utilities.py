from atomium.structures import Chain, Residue
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



class BindingResidueTests(DjangoTest):

    def setUp(self):
        self.atom = Mock()
        self.atoms = [Mock(), Mock(), Mock(), Mock()]
        self.residues = [Mock(), Mock()]
        self.residues[0].atoms.return_value = self.atoms[:2]
        self.residues[1].atoms.return_value = self.atoms[2:]
        self.atom.nearby_residues.return_value = self.residues
        self.atom.nearby_atoms.return_value = self.atoms[::2]


    def test_can_get_nearby_to_zinc(self):
        self.atom.element = "ZN"
        nearby = get_atom_binding_residues(self.atom)
        self.atom.nearby_residues.assert_called_with(
         cutoff=3, is_metal=False, element_regex="[NOS]", ligands=True
        )
        self.atom.nearby_atoms.assert_called_with(
         cutoff=3, is_metal=False, element_regex="[NOS]"
        )
        self.assertTrue(self.atoms[0].liganding)
        self.assertTrue(self.atoms[2].liganding)
        self.assertFalse(self.atoms[1].liganding)
        self.assertFalse(self.atoms[3].liganding)


    def test_can_get_nearby_to_other_metals(self):
        self.atom.element = "FE"
        nearby = get_atom_binding_residues(self.atom)
        self.atom.nearby_residues.assert_called_with(
         cutoff=3, is_metal=False, element_regex="[^C]", ligands=True
        )
        self.atom.nearby_atoms.assert_called_with(
         cutoff=3, is_metal=False, element_regex="[^C]"
        )
        self.assertTrue(self.atoms[0].liganding)
        self.assertTrue(self.atoms[2].liganding)
        self.assertFalse(self.atoms[1].liganding)
        self.assertFalse(self.atoms[3].liganding)



class ClusterUniquenessChecking(DjangoTest):

    def setUp(self):
        self.clusters = [{"residues": {1, 2, 3}}, {"residues": {4, 5, 6}}]


    def test_can_accept_uniqueness(self):
        self.assertTrue(check_clusters_have_unique_residues(self.clusters))


    def test_can_reject_duplicates(self):
        self.clusters[1]["residues"].add(1)
        self.assertFalse(check_clusters_have_unique_residues(self.clusters))



class MetalMergingTests(DjangoTest):

    def setUp(self):
        self.metals = [Mock() for _ in range(5)]
        self.residues = [Mock() for _ in range(15)]
        self.d = {metal: set(self.residues[i * 3: (i + 1) * 3])
         for i, metal in enumerate(self.metals)}


    def test_can_make_cluster_per_metal_if_nothing_in_common(self):
        clusters = merge_metal_groups(self.d)
        self.assertEqual(clusters, [
         {"metals": {self.metals[0]}, "residues": set(self.residues[:3])},
         {"metals": {self.metals[1]}, "residues": set(self.residues[3:6])},
         {"metals": {self.metals[2]}, "residues": set(self.residues[6:9])},
         {"metals": {self.metals[3]}, "residues": set(self.residues[9:12])},
         {"metals": {self.metals[4]}, "residues": set(self.residues[12:])},
        ])


    def test_can_cluster_metals_together(self):
        self.d[self.metals[2]].add(self.residues[0])
        clusters = merge_metal_groups(self.d)
        self.assertEqual(clusters, [
         {"metals": {self.metals[0], self.metals[2]}, "residues": set(
          self.residues[:3] + self.residues[6:9]
         )},
         {"metals": {self.metals[1]}, "residues": set(self.residues[3:6])},
         {"metals": {self.metals[3]}, "residues": set(self.residues[9:12])},
         {"metals": {self.metals[4]}, "residues": set(self.residues[12:])},
        ])


class ZincClusteringTests(DjangoTest):

    def setUp(self):
        self.metals = [Mock(element="ZN") for _ in range(8)]
        self.metals[3].element = "CU"
        self.metals[5].element = "FE"
        self.metals[6].element = "CU"
        self.metals[7].element = "FE"


    @patch("zinc.utilities.get_atom_binding_residues")
    @patch("zinc.utilities.merge_metal_groups")
    def test_can_cluster_zinc_from_metals(self, mock_merge, mock_res):
        mock_res.side_effect = lambda a: [a, a]
        mock_merge.return_value = [
         {"metals": set(self.metals[i * 2:(i + 1) * 2])} for i in range(4)
        ]
        clusters = cluster_zincs_with_residues(self.metals)
        for metal in self.metals:
            mock_res.assert_any_call(metal)
        mock_merge.assert_called_with({metal: [metal] * 2 for metal in self.metals})
        self.assertEqual(clusters, mock_merge.return_value[:3])
