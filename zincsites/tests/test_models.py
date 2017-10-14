from datetime import datetime
from django.core.exceptions import ValidationError
from unittest.mock import patch
from zincdb.tests import ModelTest
from zincsites.models import ZincSite, Pdb, Residue

class ZincSiteTests(ModelTest):

    def setUp(self):
        ModelTest.setUp(self)
        date = datetime(1970, 1, 1).date()
        self.pdb = Pdb(id="1XXX", title="The PDB Title", deposition_date=date)
        self.pdb.save()
        self.residue1 = Residue(
         id="1XXXA12", residue_id="A12", chain="A", name="VAL", pdb=self.pdb
        )
        self.residue1.save()
        self.residue2 = Residue(
         id="1XXXA15", residue_id="A15", chain="A", name="VAL", pdb=self.pdb
        )
        self.residue2.save()


    def test_save_and_retrieve_zinc_sites(self):
        self.assertEqual(ZincSite.objects.all().count(), 1)
        site = ZincSite(id="1XXXA999")
        site.save()
        site.residues.add(self.residue1)
        site.residues.add(self.residue2)
        site.save()
        self.assertEqual(ZincSite.objects.all().count(), 2)
        retrieved_site = ZincSite.objects.last()
        self.assertEqual(retrieved_site, site)
        self.assertEqual(site.residues.all().count(), 2)
        self.assertEqual(self.residue1.zincsite_set.all().count(), 1)
        self.assertEqual(self.residue2.zincsite_set.all().count(), 1)
        self.assertEqual(site.pdb, self.pdb)



class PdbTests(ModelTest):

    def test_save_and_retrieve_pdbs(self):
        date = datetime(1970, 1, 1).date()
        self.assertEqual(Pdb.objects.all().count(), 1)
        pdb = Pdb(id="1XXY", title="The PDB Title", deposition_date=date)
        pdb.save()
        self.assertEqual(Pdb.objects.all().count(), 2)
        retrieved_pdb = Pdb.objects.last()
        self.assertEqual(retrieved_pdb, pdb)



class ResidueTests(ModelTest):

    def test_save_and_retrieve_residues(self):
        date = datetime(1970, 1, 1).date()
        self.assertEqual(Residue.objects.all().count(), 2)
        pdb = Pdb.objects.first()
        residue = Residue(id="1XXYA12", residue_id="A12", chain="A", name="VAL", pdb=pdb)
        residue.save()
        self.assertEqual(Residue.objects.all().count(), 3)
        retrieved_residue = Residue.objects.get(residue_id="A12")
        self.assertEqual(retrieved_residue, residue)
        self.assertEqual(pdb.residue_set.all().first(), residue)
