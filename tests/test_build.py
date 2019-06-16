import sys; sys.path.append("build")
from datetime import date
from collections import Counter
from unittest.mock import patch, Mock, MagicMock
from django.test import LiveServerTestCase
from core.models import Pdb, Chain, ZincSite, ChainCluster, Group
from build.build import main as build_main
from build.cluster import main as cluster_main

class DatabaseBuildingTests(LiveServerTestCase):

    def setUp(self):
        self.patch1 = patch("build.build.get_zinc_pdb_codes")
        self.patch2 = patch("builtins.print")
        self.patch3 = patch("build.build.tqdm")
        self.patch4 = patch("build.build.log")
        self.mock_codes = self.patch1.start()
        self.mock_print = self.patch2.start()
        self.mock_tqdm = self.patch3.start()
        self.mock_log = self.patch4.start()
        self.mock_tqdm.side_effect = lambda l: l


    def tearDown(self):
        self.patch1.stop()
        self.patch2.stop()
        self.patch3.stop()
        self.patch4.stop()


    def check_print_statement(self, fragment):
        for call in self.mock_print.call_args_list:
            if fragment in call[0][0]: break
        else:
            raise ValueError(f"No print call with '{fragment}' in")


    def test_script_checking_only_new(self):
        Pdb.objects.create(id="1SP1", skeleton=False)
        self.mock_codes.return_value = ["1SP1", "3ZNF"]
        build_main()
        self.check_print_statement("There are 2 PDB codes with zinc")
        self.check_print_statement("1 of these need to be checked")


    def test_can_get_best_model(self):
        self.mock_codes.return_value = ["1B21"]
        build_main()
        pdb = Pdb.objects.get(id="1B21")
        self.assertIn("BURIED SALT BRIDGE", pdb.title)
        self.assertEqual(pdb.assembly, 3)


    def test_can_reject_skeleton_models(self):
        self.mock_codes.return_value = ["4UXY"]
        build_main()
        pdb = Pdb.objects.get(id="4UXY")
        self.assertIn("ATP binding", pdb.title)
        self.assertTrue(pdb.skeleton)
        self.assertEqual(pdb.metal_set.count(), 1)
        metal = pdb.metal_set.first()
        self.assertEqual(metal.atomium_id, 1171)
        self.assertEqual(metal.residue_number, 1413)
        self.assertEqual(metal.chain_id, "A")
        self.assertIn("no side chain", metal.omission_reason.lower())
    

    def test_zincs_not_in_model_are_still_saved(self):
        self.mock_codes.return_value = ["6H8P"]
        build_main()
        pdb = Pdb.objects.get(id="6H8P")
        self.assertIn("JMJD2A/ KDM4A", pdb.title)
        self.assertEqual(pdb.assembly, 2)
        self.assertFalse(pdb.skeleton)
        self.assertEqual(pdb.metal_set.count(), 2)
        used_zinc = pdb.metal_set.filter(omission_reason=None)
        self.assertEqual(used_zinc.count(), 1)
        self.assertEqual(used_zinc.first().atomium_id, 11222)
        tossed_zinc = pdb.metal_set.exclude(omission_reason=None)
        self.assertEqual(tossed_zinc.count(), 1)
        self.assertEqual(tossed_zinc.first().atomium_id, 11164)
    

    def test_superimposed_atoms_are_dealt_with(self):
        self.mock_codes.return_value = ["1XDA"]
        build_main()
        pdb = Pdb.objects.get(id="1XDA")
        self.assertEqual(pdb.assembly, 5)
        self.assertEqual(pdb.metal_set.filter(omission_reason=None).count(), 2)
        self.assertEqual(
         pdb.metal_set.filter(omission_reason=None).first().coordinatebond_set.count(), 4
        )
    
    
    def test_can_reject_liganding_atoms_with_too_acute_angle(self):
        self.mock_codes.return_value = ["2AHJ"]
        build_main()
        pdb = Pdb.objects.get(id="2AHJ")
        for site in pdb.zincsite_set.all():
            if site.metal_set.first().chain_id == "C":
                self.assertEqual(site.metal_set.first().coordinatebond_set.count(), 4)
    

    def test_can_handle_sites_having_too_few_liganding_atoms(self):
        self.mock_codes.return_value = ["1A0Q"]
        build_main()
        pdb = Pdb.objects.get(id="1A0Q")
        self.assertEqual(pdb.metal_set.count(), 3)
        self.assertEqual(pdb.zincsite_set.count(), 1)
        bad_zincs = pdb.metal_set.exclude(omission_reason=None)
        for zinc in bad_zincs:
            self.assertIn("few", zinc.omission_reason)
    

    def test_can_handle_multi_metal_sites(self):
        self.mock_codes.return_value = ["6A5K"]
        build_main()
        pdb = Pdb.objects.get(id="6A5K")
        multi_site = pdb.zincsite_set.get(family="C9")
        self.assertEqual(multi_site.metal_set.count(), 3)
        for metal in multi_site.metal_set.all():
            self.assertEqual(metal.coordinatebond_set.count(), 4)
    

    def test_can_ignore_sites_without_zinc(self):
        self.mock_codes.return_value = ["1A85"]
        build_main()
        pdb = Pdb.objects.get(id="1A85")
        self.assertEqual(pdb.zincsite_set.count(), 2)
    

    def test_can_create_chains_properly(self):
        self.mock_codes.return_value = ["1B0N"]
        build_main()
        pdb = Pdb.objects.get(id="1B0N")
        self.assertEqual(pdb.assembly, 2)
        self.assertEqual(pdb.chain_set.count(), 2)
        chain_a = pdb.chain_set.get(atomium_id="A")
        self.assertEqual(len([r for r in chain_a.sequence if r.isupper()]), 7)
        chain_b = pdb.chain_set.get(atomium_id="B")
        self.assertEqual(len([r for r in chain_b.sequence if r.isupper()]), 4)
        site = pdb.zincsite_set.get(id="1B0N-1")
        self.assertEqual(site.chaininteraction_set.count(), 2)
        chain_interaction_a = site.chaininteraction_set.get(chain=chain_a)
        self.assertEqual(len([r for r in chain_interaction_a.sequence if r.isupper()]), 2)
        chain_interaction_b = site.chaininteraction_set.get(chain=chain_b)
        self.assertEqual(len([r for r in chain_interaction_b.sequence if r.isupper()]), 3)
    

    def test_can_work_properly(self):
        self.mock_codes.return_value = ["6EQU"]
        build_main()
        pdb = Pdb.objects.get(id="6EQU")
        self.assertIn("anhydrase II", pdb.title)
        self.assertEqual(pdb.assembly, 1)
        self.assertFalse(pdb.skeleton)
        self.assertEqual(pdb.classification, "LYASE")
        self.assertEqual(pdb.deposition_date, date(2017, 10, 15))
        self.assertEqual(pdb.expression_system, "Escherichia coli BL21(DE3)")
        self.assertEqual(pdb.organism, "Homo sapiens")
        self.assertEqual(
         pdb.keywords,
         "human carbonic anhydrase II, membrane-impermeant inhibitor, complex, lyase" 
        )
        self.assertEqual(pdb.resolution, 1.65)
        self.assertEqual(pdb.rvalue, 0.1746)
        self.assertEqual(pdb.technique, "X-RAY DIFFRACTION")
        
        self.assertEqual(pdb.zincsite_set.count(), 1)
        self.assertEqual(pdb.metal_set.count(), 1)
        self.assertEqual(pdb.chain_set.count(), 1)

        chain = pdb.chain_set.first()
        self.assertEqual(chain.atomium_id, "A")
        self.assertEqual(len(chain.sequence), 261)
        self.assertEqual(chain.sequence[94:97], "HfH")

        site = pdb.zincsite_set.first()
        self.assertEqual(site.family, "H3")
        self.assertEqual(site.residue_names, ".BVE..HIS.")
        self.assertFalse(site.representative)

        metal = site.metal_set.first()
        self.assertEqual(metal, pdb.metal_set.first())
        self.assertEqual(metal.atomium_id, 2133)
        self.assertEqual(metal.residue_name, "ZN")
        self.assertEqual(metal.insertion_code, "")
        self.assertEqual(metal.chain_id, "A")
        self.assertEqual(metal.residue_number, 301)
        self.assertEqual(metal.x, -6.582)
        self.assertEqual(metal.y, -1.525)
        self.assertEqual(metal.z, 15.281)
        self.assertEqual(metal.omission_reason, None)
        
        residues = site.residue_set.all()
        self.assertEqual(residues.count(), 4)
        res1 = residues.get(atomium_id="A.94")
        self.assertEqual(res1.name, "HIS")
        self.assertEqual(res1.residue_number, 94)
        self.assertEqual(res1.insertion_code, "")
        self.assertEqual(res1.chain_identifier, "A")
        self.assertEqual(res1.chain_signature, "phe.HIS.phe")
        self.assertEqual(res1.chain, chain)
        self.assertEqual(res1.atom_set.count(), 10)
        res4 = residues.get(atomium_id="A.302")
        self.assertEqual(res4.name, "BVE")
        self.assertEqual(res4.residue_number, 302)
        self.assertEqual(res4.insertion_code, "")
        self.assertEqual(res4.chain_identifier, "A")
        self.assertEqual(res4.chain_signature, "")
        self.assertIsNone(res4.chain)
        self.assertEqual(res4.atom_set.count(), 36)

        bonds = metal.coordinatebond_set.all()
        self.assertEqual(bonds.count(), 5)
        bound_res_ids = Counter([b.atom.residue.atomium_id for b in bonds])
        self.assertEqual(bound_res_ids, {"A.94": 1, "A.96": 1, "A.119": 1, "A.302": 2})

        chain_interactions = site.chaininteraction_set.all()
        self.assertEqual(chain_interactions.count(), 1)
        interaction = chain_interactions.first()
        self.assertEqual(len(interaction.sequence), 261)
        self.assertEqual(interaction.sequence[94:97], "HfH")



class DatabaseClusteringTests(LiveServerTestCase):

    fixtures = ["pre-cluster.json"]

    @patch("builtins.print")
    @patch("build.cluster.tqdm")
    @patch("build.sites.tqdm")
    def test_can_cluster(self, mock_tqdm1, mock_tqdm2, mock_print):
        mock_tqdm1.side_effect = lambda l: l
        mock_tqdm2.side_effect = lambda l: l

        # The database is primed
        self.assertEqual(Chain.objects.count(), 15)
        self.assertEqual(ZincSite.objects.count(), 19)
        self.assertEqual(ChainCluster.objects.count(), 0)
        self.assertEqual(Group.objects.count(), 0)
        for site in ZincSite.objects.all():
            self.assertFalse(site.representative)

        # Cluster
        cluster_main()

        # Chain clusters are correct
        self.assertEqual(ChainCluster.objects.count(), 5)
        anhydrase_cluster = ChainCluster.objects.get(id="12CAA")
        anhydrase_chains = anhydrase_cluster.chain_set.all()
        self.assertEqual(anhydrase_chains.count(), 3)
        insulin_cluster = ChainCluster.objects.get(id="1IZBB")
        insulin_chains = insulin_cluster.chain_set.all()
        self.assertEqual(insulin_chains.count(), 6)
        dehydro_cluster = ChainCluster.objects.get(id="3HUDA")
        dehydro_chains = dehydro_cluster.chain_set.all()
        self.assertEqual(dehydro_chains.count(), 4)

        # Groupsare correct
        self.assertEqual(Group.objects.count(), 6)
        anhydrase = Group.objects.get(id="12CA-1")
        anhydrase_sites = anhydrase.zincsite_set.all()
        self.assertEqual(anhydrase_sites.count(), 3)
        insulin = Group.objects.get(id="1IZB-1")
        insulin_sites = insulin.zincsite_set.all()
        self.assertEqual(insulin_sites.count(), 6)
        dehydro = Group.objects.get(id="3HUD-1")
        dehydro_sites = dehydro.zincsite_set.all()
        self.assertEqual(dehydro_sites.count(), 4)

