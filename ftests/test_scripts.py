from unittest.mock import patch, Mock, MagicMock
from testarsenal import DjangoTest
from core.models import *
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
        self.mock_codes.return_value = [
         "6EQU", #standard
         "1B21", # no zinc in best assembly
         "4UXY", # skeleton
         "6H8P", # some zincs not in assembly
         "1ZEH", # zincs superimposed onto each other in assembly
         "1A6F", # sites duplicated in assembly
         "1BYF", # zinc with no residues
         "1A0Q", # zinc with too few liganding atoms
        ]


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
        main(json=False)
        self.check_print_statement("There are 2 PDBs with zinc")
        self.check_print_statement("1 are going to be checked")
        self.mock_codes.return_value = ["1SP1", "3ZNF", "1PAA"]


    def test_can_get_best_model(self):
        self.mock_codes.return_value = ["1B21"]
        main(json=False)
        pdb = Pdb.objects.get(id="1B21")
        self.assertIn("BURIED SALT BRIDGE", pdb.title)
        self.assertEqual(pdb.assembly, 3)
        self.assertEqual(pdb.metal_set.count(), 1)


    def test_can_reject_skeleton_models(self):
        self.mock_codes.return_value = ["4UXY"]
        main(json=False)
        pdb = Pdb.objects.get(id="4UXY")
        self.assertIn("ATP binding", pdb.title)
        self.assertTrue(pdb.skeleton)
        self.assertEqual(pdb.metal_set.count(), 1)
        metal = pdb.metal_set.first()
        self.assertEqual(metal.atom_pdb_identifier, 1171)
        self.assertEqual(metal.residue_pdb_identifier, 1413)
        self.assertEqual(metal.chain_pdb_identifier, "A")
        self.assertIn("no side chain", metal.omission.lower())
        self.assertEqual(pdb.zincsite_set.count(), 0)
        self.assertEqual(len(pdb.chains), 0)


    def test_can_store_zincs_not_in_assembly(self):
        self.mock_codes.return_value = ["6H8P"]
        main(json=False)
        pdb = Pdb.objects.get(id="6H8P")
        self.assertIn("JMJD2A/ KDM4A", pdb.title)
        self.assertEqual(pdb.assembly, 2)
        self.assertFalse(pdb.skeleton)
        self.assertEqual(pdb.metal_set.count(), 2)
        self.assertEqual(pdb.zincsite_set.count(), 1)
        self.assertEqual(len(pdb.chains), 1)
        used_zinc = pdb.metal_set.filter(omission=None)
        self.assertEqual(used_zinc.count(), 1)
        self.assertEqual(used_zinc.first().atom_pdb_identifier, 11222)
        tossed_zinc = pdb.metal_set.exclude(omission=None)
        self.assertEqual(tossed_zinc.count(), 1)
        self.assertEqual(tossed_zinc.first().atom_pdb_identifier, 11164)


    def test_can_reject_liganding_atoms_with_too_acute_angle(self):
        self.mock_codes.return_value = ["2AHJ"]
        main(json=False)
        pdb = Pdb.objects.get(id="2AHJ")
        for site in pdb.zincsite_set.all():
            if site.metal_set.first().chain_pdb_identifier == "C":
                self.assertEqual(site.metal_set.first().coordination, 4)


    def test_can_handle_multi_metal_sites(self):
        self.mock_codes.return_value = ["6A5K"]
        main(json=False)
        pdb = Pdb.objects.get(id="6A5K")
        multi_site = pdb.zincsite_set.get(family="C9")
        self.assertEqual(multi_site.metal_set.count(), 3)
        for metal in multi_site.metal_set.all():
            self.assertEqual(metal.coordinatebond_set.count(), 4)


    def test_can_handle_zincs_superimposed_onto_each_other(self):
        self.mock_codes.return_value = ["1ZEH"]
        main(json=False)
        pdb = Pdb.objects.get(id="1ZEH")
        self.assertIn("STRUCTURE OF INSULIN", pdb.title)
        self.assertEqual(pdb.assembly, 3)
        self.assertEqual(pdb.metal_set.count(), 2)
        self.assertEqual(pdb.zincsite_set.count(), 2)
        site1 = pdb.metal_set.get(atom_pdb_identifier=846).site
        self.assertEqual(site1.residue_set.count(), 4)
        self.assertEqual(
         set([r.chain.chain_pdb_identifier for r in site1.residue_set.all()]),
         {"B"}
        )
        self.assertEqual(site1.copies, 1)
        site2 = pdb.metal_set.get(atom_pdb_identifier=856).site
        self.assertEqual(site2.residue_set.count(), 4)
        self.assertEqual(
         set([r.chain.chain_pdb_identifier for r in site2.residue_set.all()]),
         {"D"}
        )
        self.assertEqual(site2.copies, 1)


    def test_can_handle_sites_being_duplicated_in_assembly(self):
        self.mock_codes.return_value = ["1A6F"]
        main(json=False)
        pdb = Pdb.objects.get(id="1A6F")
        self.assertIn("RNASE P PROTEIN FROM BACILLUS SUBTILIS", pdb.title)
        self.assertEqual(pdb.assembly, 2)
        self.assertEqual(pdb.metal_set.count(), 2)
        self.assertEqual(pdb.zincsite_set.count(), 2)
        site1 = pdb.metal_set.get(atom_pdb_identifier=951).site
        self.assertEqual(site1.residue_set.count(), 6)
        self.assertEqual(site1.copies, 1)
        site2 = pdb.metal_set.get(atom_pdb_identifier=952).site
        self.assertEqual(site2.residue_set.count(), 3)
        self.assertEqual(site2.copies, 2)


    def test_can_handle_sites_having_too_few_residues(self):
        self.mock_codes.return_value = ["1BYF"]
        main(json=False)
        pdb = Pdb.objects.get(id="1BYF")
        self.assertIn("POLYANDROCARPA", pdb.title)
        self.assertEqual(pdb.assembly, 2)
        self.assertEqual(pdb.metal_set.count(), 7)
        bad_zinc = pdb.metal_set.exclude(omission=None).first()
        self.assertIn("residues", bad_zinc.omission)


    def test_can_handle_sites_having_too_few_liganding_atoms(self):
        self.mock_codes.return_value = ["1A0Q"]
        main(json=False)
        pdb = Pdb.objects.get(id="1A0Q")
        self.assertIn("29G11 COMPLEXED", pdb.title)
        self.assertEqual(pdb.metal_set.count(), 3)
        self.assertEqual(pdb.zincsite_set.count(), 1)
        bad_zinc = pdb.metal_set.exclude(omission=None).first()
        self.assertIn("few", bad_zinc.omission)
        self.assertEqual(len(set([m.atomium_id for m in pdb.metal_set.all()])), 3)


    def test_script_can_function_normally(self):
        self.mock_codes.return_value = ["6EQU"]
        main(json=False)
        pdb = Pdb.objects.get(id="6EQU")
        self.assertIn("anhydrase II", pdb.title)
        self.assertEqual(pdb.assembly, 1)
        self.assertFalse(pdb.skeleton)
        self.assertEqual(pdb.metal_set.count(), 1)
        metal = pdb.metal_set.first()
        self.assertEqual(metal.atom_pdb_identifier, 2133)
        self.assertEqual(metal.residue_pdb_identifier, 301)
        self.assertEqual(metal.chain_pdb_identifier, "A")
        self.assertEqual(metal.residue_name, "ZN")
        self.assertEqual(metal.element, "ZN")
        self.assertEqual(pdb.zincsite_set.count(), 1)
        site = pdb.zincsite_set.first()
        self.assertEqual(site.metal_set.count(), 1)
        self.assertEqual(site.metal_set.first(), metal)
        self.assertEqual(site.copies, 1)
        self.assertEqual(site.residue_set.count(), 4)
        self.assertEqual(
         set([r.name for r in site.residue_set.all()]), {"HIS", "BVE"}
        )
        self.assertEqual(
         set([r.residue_pdb_identifier for r in site.residue_set.all()]),
         {119, 94, 96, 302}
        )
        res = site.residue_set.get(residue_pdb_identifier=94)
        self.assertEqual(res.atom_set.count(), 10)
        self.assertEqual(len(pdb.chains), 1)
        chain = pdb.chains[0]
        self.assertEqual(chain.chain_pdb_identifier, "A")
        self.assertTrue(chain.sequence.startswith("gmshhwgy"))
        for res in site.residue_set.all():
            self.assertEqual(res.chain, chain)


    def spit_out_json(self):
        from django.core.management import call_command
        main(json=False)
        call_command(
         "dumpdata", "--all", "--exclude=contenttypes", "--output=ftests/testdb.json", verbosity=0
        )
