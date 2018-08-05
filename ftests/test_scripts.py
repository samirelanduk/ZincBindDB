from unittest.mock import patch, Mock, MagicMock
from testarsenal import DjangoTest
from zinc.models import *
from scripts.build_db import main

class DatabaseBuildingTests(DjangoTest):

    def setUp(self):
        self.patch1 = patch("scripts.build_db.get_zinc_pdb_codes")
        self.patch2 = patch("builtins.print")
        self.patch3 = patch("scripts.build_db.tqdm")
        self.patch4 = patch("logging.getLogger")
        self.mock_codes = self.patch1.start()
        self.mock_print = self.patch2.start()
        self.mock_tqdm = self.patch3.start()
        self.mock_logging = self.patch4.start()
        self.mock_tqdm.side_effect = lambda l: l
        self.mock_codes.return_value = [
         "6EQU", #standard
         "5IV5", # mmCIF only
         "1B21", # no zinc in best assembly
         "4UXY", # skeleton
         "1A2P", # some zincs not in assembly
         "1ZEH", # zincs superimposed onto each other in assembly
         "1A6F", # sites duplicated in assembly
         "6GFB", # zinc with no residues
        ]


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


    def test_script(self):
        main(log=False, json=False)

        # The right things are printed
        self.check_print_statement("There are 8 PDBs with zinc")
        self.check_print_statement("0 have already been checked")

        # The database has the right number of things in it
        self.assertEqual(Pdb.objects.count(), 7)

        # 6EQU is fine
        pdb = Pdb.objects.get(id="6EQU")
        self.assertIn("ANHYDRASE II", pdb.title)
        self.assertEqual(pdb.assembly, 1)
        self.assertFalse(pdb.skeleton)
        self.assertEqual(pdb.metal_set.count(), 1)
        metal = pdb.metal_set.first()
        self.assertEqual(metal.atom_pdb_identifier, 2134)
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
        self.assertEqual(res.atom_set.filter(liganding=True).count(), 1)
        self.assertEqual(pdb.chain_set.count(), 1)
        chain = pdb.chain_set.first()
        self.assertEqual(chain.chain_pdb_identifier, "A")
        self.assertTrue(chain.sequence.startswith("GMSHHWGY"))
        for res in site.residue_set.all():
            self.assertEqual(res.chain, chain)

        # 1B21 is fine
        pdb = Pdb.objects.get(id="1B21")
        self.assertIn("BURIED SALT BRIDGE", pdb.title)
        self.assertEqual(pdb.assembly, 3)
        self.assertEqual(pdb.metal_set.count(), 1)

        # 4UXY is fine
        pdb = Pdb.objects.get(id="4UXY")
        self.assertIn("ATP BINDING", pdb.title)
        self.assertTrue(pdb.skeleton)
        self.assertEqual(pdb.metal_set.count(), 1)
        metal = pdb.metal_set.first()
        self.assertEqual(metal.atom_pdb_identifier, 1174)
        self.assertEqual(metal.residue_pdb_identifier, 1413)
        self.assertEqual(metal.chain_pdb_identifier, "A")
        self.assertIn("no residue", metal.omission.lower())
        self.assertEqual(pdb.zincsite_set.count(), 0)
        self.assertEqual(pdb.chain_set.count(), 0)

        # 1A2P is fine
        pdb = Pdb.objects.get(id="1A2P")
        self.assertIn("BARNASE WILDTYPE", pdb.title)
        self.assertEqual(pdb.assembly, 1)
        self.assertFalse(pdb.skeleton)
        self.assertEqual(pdb.metal_set.count(), 3)
        self.assertEqual(pdb.zincsite_set.count(), 1)
        self.assertEqual(pdb.chain_set.count(), 1)
        used_zinc = pdb.metal_set.filter(omission=None)
        self.assertEqual(used_zinc.count(), 1)
        self.assertEqual(used_zinc.first().atom_pdb_identifier, 2628)
        tossed_zinc = pdb.metal_set.exclude(omission=None)
        self.assertEqual(tossed_zinc.count(), 2)
        self.assertEqual(
         set(tossed_zinc.values_list("atom_pdb_identifier", flat=True)),
         {2629, 2630}
        )
        self.assertEqual(pdb.chain_set.count(), 1)

        # 1ZEH is fine
        pdb = Pdb.objects.get(id="1ZEH")
        self.assertIn("STRUCTURE OF INSULIN", pdb.title)
        self.assertEqual(pdb.assembly, 3)
        self.assertEqual(pdb.metal_set.count(), 2)
        self.assertEqual(pdb.zincsite_set.count(), 2)
        site1 = pdb.metal_set.get(atom_pdb_identifier=850).site
        self.assertEqual(site1.residue_set.count(), 3)
        self.assertEqual(
         set([r.chain.chain_pdb_identifier for r in site1.residue_set.all()]),
         {"B"}
        )
        self.assertEqual(site1.copies, 1)
        site2 = pdb.metal_set.get(atom_pdb_identifier=860).site
        self.assertEqual(site1.residue_set.count(), 3)
        self.assertEqual(
         set([r.chain.chain_pdb_identifier for r in site2.residue_set.all()]),
         {"D"}
        )
        self.assertEqual(site2.copies, 1)

        # 1A6F is fine
        pdb = Pdb.objects.get(id="1A6F")
        self.assertIn("RNASE P PROTEIN FROM BACILLUS SUBTILIS", pdb.title)
        self.assertEqual(pdb.assembly, 2)
        self.assertEqual(pdb.metal_set.count(), 2)
        self.assertEqual(pdb.zincsite_set.count(), 2)
        site1 = pdb.metal_set.get(atom_pdb_identifier=952).site
        self.assertEqual(site1.residue_set.count(), 8)
        self.assertEqual(site1.copies, 1)
        site2 = pdb.metal_set.get(atom_pdb_identifier=953).site
        self.assertEqual(site2.residue_set.count(), 3)
        self.assertEqual(site2.copies, 2)

        # 6GFB is fine
        pdb = Pdb.objects.get(id="6GFB")
        self.assertIn("BTB/POZ DOMAIN", pdb.title)
        self.assertEqual(pdb.assembly, 1)
        self.assertEqual(pdb.metal_set.count(), 3)
        self.assertEqual(pdb.zincsite_set.count(), 2)
        bad_zinc = pdb.metal_set.exclude(omission=None).first()
        self.assertIn("residues", bad_zinc.omission)
