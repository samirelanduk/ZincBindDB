from datetime import datetime
from mixer.backend.django import mixer
from django.core.exceptions import ValidationError
from unittest.mock import patch, Mock, MagicMock
from zincdb.tests import ModelTest
from zincsites.models import ZincSite, Pdb, Residue

class PdbTests(ModelTest):

    def test_can_create_pdb(self):
        pdb = Pdb(pk="1XXY", title="The PDB Title", deposition_date=self.date)
        pdb.full_clean()
        pdb.save()
        self.assertEqual(Pdb.objects.all().count(), 1)
        retrieved_pdb = Pdb.objects.first()
        self.assertEqual(retrieved_pdb, pdb)


    def test_pdb_title_is_needed(self):
        with self.assertRaises(ValidationError):
            pdb = Pdb(pk="1XXY", title="", deposition_date=self.date)
            pdb.full_clean()


    def test_pdb_date_is_needed(self):
        with self.assertRaises(ValidationError):
            pdb = Pdb(pk="1XXY", title="Title", deposition_date=None)
            pdb.full_clean()



class ResidueTests(ModelTest):

    def setUp(self):
        self.pdb = mixer.blend(Pdb)


    def test_can_create_residue(self):
        residue = Residue(
         pk="1RRRA1", residue_id="A12", number=12,
         chain="A", name="VAL", pdb=self.pdb
        )
        self.assertEqual(residue.zincsite_set.count(), 0)
        residue.full_clean()
        residue.save()
        self.assertEqual(Residue.objects.all().count(), 1)
        retrieved_residue = Residue.objects.first()
        self.assertEqual(retrieved_residue, residue)


    def test_residue_id_is_needed(self):
        with self.assertRaises(ValidationError):
            residue = Residue(
             pk="1RRRA1", residue_id="", number=12,
             chain="A", name="VAL", pdb=self.pdb
            )
            residue.full_clean()


    def test_residue_number_is_needed(self):
        with self.assertRaises(ValidationError):
            residue = Residue(
             pk="1RRRA1", residue_id="A1", number=None,
             chain="A", name="VAL", pdb=self.pdb
            )
            residue.full_clean()


    def test_residue_chain_is_needed(self):
        with self.assertRaises(ValidationError):
            residue = Residue(
             pk="1RRRA1", residue_id="A1", number=12,
             chain="", name="VAL", pdb=self.pdb
            )
            residue.full_clean()


    def test_residue_name_is_needed(self):
        with self.assertRaises(ValidationError):
            residue = Residue(
             pk="1RRRA1", residue_id="A1", number=12,
             chain="A", name="", pdb=self.pdb
            )
            residue.full_clean()


    def test_residue_pdb_is_needed(self):
        with self.assertRaises(ValidationError):
            residue = Residue(
             pk="1RRRA1", residue_id="A1", number=12,
             chain="A", name="", pdb=None
            )
            residue.full_clean()


    def test_residue_ordering(self):
        for chain in ["B", "A"]:
            for number in [11, 9, 10]:
                residue = Residue(
                 pk="1RRR{}{}".format(chain, number), residue_id="A1",
                 number=number, chain=chain, name="VAL", pdb=self.pdb
                )
                residue.save()
        self.assertEqual(Residue.objects.all().count(), 6)
        self.assertEqual(
         [res.id for res in Residue.objects.all()],
         ["1RRRA9", "1RRRA10", "1RRRA11", "1RRRB9", "1RRRB10", "1RRRB11"]
        )



class ZincSiteTests(ModelTest):

    def test_can_create_zinc_site(self):
        site = ZincSite(pk="1ZZZA500")
        self.assertEqual(site.residues.count(), 0)
        site.full_clean()
        site.save()
        self.assertEqual(ZincSite.objects.all().count(), 1)
        retrieved_site = ZincSite.objects.first()
        self.assertEqual(retrieved_site, site)


    @patch("zincsites.models.ZincSite.residues")
    def test_zinc_site_pdb_property(self, mock_residues):
        site = ZincSite(pk="1ZZZA500")
        site.save()
        pdb = Mock(name="pdb")
        residue = Mock(name="residue")
        residue.pdb = pdb
        residue_set = Mock(name="residue_set")
        residue_set.first = MagicMock()
        residue_set.first.return_value = residue
        site.residues = residue_set
        self.assertIs(site.pdb, pdb)
