from datetime import datetime
from mixer.backend.django import mixer
from django.core.exceptions import ValidationError
from unittest.mock import patch, Mock, MagicMock
from .base import ZincBindTest
from zincbind.models import Pdb, Residue

class PdbTests(ZincBindTest):

    def test_can_create_pdb(self):
        pdb = Pdb(
         pk="1XXY", title="The PDB Title", deposited="1990-09-28",
         resolution=4.5, checked="2017-01-01"
        )
        pdb.full_clean()


    def test_title_is_required(self):
        pdb = Pdb(
         pk="1XXY", title=None, deposited="1990-09-28",
         resolution=4.5, checked="2017-01-01"
        )
        with self.assertRaises(ValidationError):
            pdb.full_clean()
        pdb = Pdb(
         pk="1XXY", title="", deposited="1990-09-28",
         resolution=4.5, checked="2017-01-01"
        )
        with self.assertRaises(ValidationError):
            pdb.full_clean()


    def test_date_is_required(self):
        pdb = Pdb(
         pk="1XXY", title="The PDB Title", deposited=None,
         resolution=4.5, checked="2017-01-01"
        )
        with self.assertRaises(ValidationError):
            pdb.full_clean()


    def test_resolution_is_required(self):
        pdb = Pdb(
         pk="1XXY", title="The PDB Title", deposited="1990-09-28",
         resolution=None, checked="2017-01-01"
        )
        with self.assertRaises(ValidationError):
            pdb.full_clean()
        pdb = Pdb(
         pk="1XXY", title="The PDB Title", deposited="1990-09-28",
         resolution=0, checked="2017-01-01"
        )
        pdb.full_clean()


    def test_checked_can_be_null(self):
        pdb = Pdb(
         pk="1XXY", title="The PDB Title", deposited="1990-09-28",
         resolution=4.5, checked=None
        )
        pdb.full_clean()



class ResidueTests(ZincBindTest):

    def setUp(self):
        ZincBindTest.setUp(self)
        self.pdb = mixer.blend(Pdb)


    def test_can_create_residue(self):
        residue = Residue(
         pk="1XYZA10", residue_id="A10", name="VAL", chain="A", number=10,
         pdb=self.pdb
        )
        residue.full_clean()


    def test_residueid_is_required(self):
        residue = Residue(
         pk="1XYZA10", residue_id=None, name="VAL", chain="A", number=10,
         pdb=self.pdb
        )
        with self.assertRaises(ValidationError):
            residue.full_clean()
        residue = Residue(
         pk="1XYZA10", residue_id="", name="VAL", chain="A", number=10,
         pdb=self.pdb
        )
        with self.assertRaises(ValidationError):
            residue.full_clean()


    def test_name_is_required(self):
        residue = Residue(
         pk="1XYZA10", residue_id="A10", name=None, chain="A", number=10,
         pdb=self.pdb
        )
        with self.assertRaises(ValidationError):
            residue.full_clean()
        residue = Residue(
         pk="1XYZA10", residue_id="A10", name="", chain="A", number=10,
         pdb=self.pdb
        )
        with self.assertRaises(ValidationError):
            residue.full_clean()


    def test_chain_is_required(self):
        residue = Residue(
         pk="1XYZA10", residue_id="A10", name="VAL", chain=None, number=10,
         pdb=self.pdb
        )
        with self.assertRaises(ValidationError):
            residue.full_clean()
        residue = Residue(
         pk="1XYZA10", residue_id="A10", name="VAL", chain="", number=10,
         pdb=self.pdb
        )
        with self.assertRaises(ValidationError):
            residue.full_clean()


    def test_number_is_required(self):
        residue = Residue(
         pk="1XYZA10", residue_id="A10", name="VAL", chain="A", number=None,
         pdb=self.pdb
        )
        with self.assertRaises(ValidationError):
            residue.full_clean()
        residue = Residue(
         pk="1XYZA10", residue_id="A10", name="VAL", chain="A", number=0,
         pdb=self.pdb
        )
        residue.full_clean()


    def test_pdb_is_required(self):
        residue = Residue(
         pk="1XYZA10", residue_id="A10", name="VAL", chain="A", number=10,
         pdb=None
        )
        with self.assertRaises(ValidationError):
            residue.full_clean()
