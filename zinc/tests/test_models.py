from datetime import date
from mixer.backend.django import mixer
from unittest.mock import patch, Mock, MagicMock
from testarsenal import DjangoTest
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError
from zinc.models import Pdb, Chain

class PdbTests(DjangoTest):

    def setUp(self):
        self.kwargs = {
         "id": "1XXY", "title": "The PDB Title", "deposited": date(1990, 9, 28),
         "resolution": 4.5, "organism": "HOMO SAPIENS", "expression": "M MUS",
         "classification": "LYASE", "technique": "XRAY", "skeleton": False,
         "rfactor": 4.5
        }


    def test_can_create_pdb(self):
        pdb = Pdb(**self.kwargs)
        pdb.full_clean(), pdb.save()


    def test_db_fields_required(self):
        for field in ["id", "title"]:
            kwargs = self.kwargs.copy()
            del kwargs[field]
            with self.assertRaises(ValidationError):
                Pdb(**kwargs).full_clean()


    def test_field_max_lengths(self):
        for field in self.kwargs:
            if isinstance(self.kwargs[field], str):
                self.kwargs[field] *= 100
                with self.assertRaises(ValidationError):
                    Pdb(**self.kwargs).full_clean()


    def test_none_fields(self):
        for field in self.kwargs:
            if field not in ["id", "title"]:
                self.kwargs[field] = None
                pdb = Pdb(**self.kwargs)
                pdb.full_clean()


    @patch("zinc.utilities.model_is_skeleton")
    def test_can_create_from_atomium_pdb(self, mock_is):
        mock_is.return_value = True
        atomium_pdb = Mock(
         code="1AAA", title="T", classification="C", deposition_date=date(1, 1, 1),
         organism="O", expression_system="E", technique="T", rfactor=1, resolution=2
        )
        pdb = Pdb.create_from_atomium(atomium_pdb)
        self.assertEqual(pdb.id, atomium_pdb.code)
        self.assertEqual(pdb.title, atomium_pdb.title)
        self.assertEqual(pdb.deposited, atomium_pdb.deposition_date)
        self.assertEqual(pdb.resolution, atomium_pdb.resolution)
        self.assertEqual(pdb.organism, atomium_pdb.organism)
        self.assertEqual(pdb.expression, atomium_pdb.expression_system)
        self.assertEqual(pdb.classification, atomium_pdb.classification)
        self.assertEqual(pdb.technique, atomium_pdb.technique)
        self.assertEqual(pdb.skeleton, True)
        self.assertEqual(pdb.rfactor, atomium_pdb.rfactor)
        mock_is.assert_called_with(atomium_pdb.model)
        atomium_pdb.code = "2AAA"
        mock_is.return_value = False
        self.assertEqual(Pdb.create_from_atomium(atomium_pdb).skeleton, False)



class ChainTests(DjangoTest):

    def setUp(self):
        self.pdb = mixer.blend(Pdb)
        self.kwargs = {
         "id": "1XXYB", "sequence": "MLLYTCDDWATTY", "pdb": self.pdb
        }


    def test_can_create_chain(self):
        chain = Chain(**self.kwargs)
        chain.full_clean(), chain.save()


    def test_db_fields_required(self):
        for field in self.kwargs:
            kwargs = self.kwargs.copy()
            del kwargs[field]
            with self.assertRaises(ValidationError):
                Chain(**kwargs).full_clean()


    def test_can_create_from_atomium_chain(self):
        atomium_chain = Mock(id="B")
        residues = [Mock(code="T"), Mock(code="M"), Mock(code="V")]
        atomium_chain.residues.return_value = residues
        pdb = mixer.blend(Pdb, id="1AAA")
        chain = Chain.create_from_atomium(atomium_chain, pdb)
        self.assertEqual(chain.id, "1AAAB")
        self.assertEqual(chain.sequence, "TMV")
        self.assertEqual(chain.pdb, pdb)
