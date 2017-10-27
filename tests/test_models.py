from datetime import datetime
from mixer.backend.django import mixer
from django.core.exceptions import ValidationError
from unittest.mock import patch, Mock, MagicMock
from .base import ZincBindTest
from zincbind.models import Pdb

class PdbTests(ZincBindTest):

    def test_can_create_pdb(self):
        pdb = Pdb(
         pk="1XXY", title="The PDB Title", deposited="1990-09-28",
         resolution=4.5, checked="2017-01-01"
        )
        pdb.full_clean()
        pdb.save()
        self.assertEqual(Pdb.objects.all().count(), 1)
        retrieved_pdb = Pdb.objects.first()
        self.assertEqual(retrieved_pdb, pdb)


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
