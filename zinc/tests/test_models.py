from datetime import date
from mixer.backend.django import mixer
from unittest.mock import patch, Mock, MagicMock
from testarsenal import DjangoTest
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError
from zinc.models import Pdb

class PdbTests(DjangoTest):

    def setUp(self):
        self.kwargs = {
         "id": "1XXY", "title": "The PDB Title", "deposited": date(1990, 9, 28),
         "resolution": 4.5, "organism": "HOMO SAPIENS", "expression": "M MUS",
         "classification": "LYASE", "technique": "XRAY", "skeleton": False,
         "rfactor": 4.5, "checked": date(2017, 1, 1)
        }


    def test_can_create_pdb(self):
        pdb = Pdb(**self.kwargs)
        pdb.full_clean(), pdb.save()


    def test_all_pdb_fields_required(self):
        for field in self.kwargs:
            kwargs = self.kwargs.copy()
            del kwargs[field]
            if field == "skeleton":
                with transaction.atomic():
                    with self.assertRaises(IntegrityError):
                        Pdb(**kwargs).save()
            else:
                with self.assertRaises(ValidationError):
                    Pdb(**kwargs).full_clean()


    def test_field_max_lengths(self):
        for field in self.kwargs:
            if isinstance(self.kwargs[field], str):
                self.kwargs[field] *= 100
                with self.assertRaises(ValidationError):
                    Pdb(**self.kwargs).full_clean()
