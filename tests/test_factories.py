from datetime import datetime
from unittest.mock import patch, Mock, MagicMock
from freezegun import freeze_time
from django.db import IntegrityError
from .base import ZincBindTest
from zincbind.factories import *
from zincbind.exceptions import DuplicateSiteError

class FactoryTest(ZincBindTest):

    def setUp(self):
        ZincBindTest.setUp(self)
        self.pdb = Mock()
        self.pdb.code.return_value = "1ABC"
        self.pdb.deposition_date.return_value = self.date
        self.pdb.title.return_value = "PDB TITLE."
        self.pdb.resolution.return_value = 4.5
        self.pdb_record = Mock()
        self.pdb_record.id = "1ABC"
        self.res1 = Mock()
        self.res1.residue_id.return_value = "B10"
        self.res1.name.return_value = "VAL"
        chain = Mock()
        chain.chain_id.return_value = "C"
        residues_list = Mock()
        residues_list.index = MagicMock()
        residues_list.index.return_value = 20
        chain.residues = MagicMock()
        chain.residues.return_value = residues_list
        self.res1.chain = MagicMock()
        self.res1.chain.return_value = chain
        self.res2 = Mock()
        self.atom1, self.atom2 = Mock(), Mock()
        self.atom1.atom_id.return_value = 1
        self.atom1.x.return_value = 15
        self.atom1.y.return_value = 16
        self.atom1.z.return_value = 17
        self.atom1.element.return_value = "N"
        self.atom1.name.return_value = "N2"
        self.atom1.charge.return_value = -1
        self.atom1.bfactor.return_value = 101
        self.atom2.atom_id.return_value = 2
        self.atom2.x.return_value = 25
        self.atom2.y.return_value = 26
        self.atom2.z.return_value = 27
        self.atom2.element.return_value = "Z"
        self.atom2.name.return_value = "Z5"
        self.atom2.charge.return_value = -2
        self.atom2.bfactor.return_value = 202
        self.res1.atoms.return_value = set([self.atom1, self.atom2])
        self.zinc = Mock()
        self.zinc.molecule_id.return_value = "B505"
        self.zinc.atom.return_value = self.atom1



class EmptyPdbCreationTests(FactoryTest):

    @freeze_time("2012-01-01 12:00:01")
    @patch("zincbind.factories.Pdb.objects.create")
    def test_can_add_empty_pdb(self, mock_create):
        create_empty_pdb("1ABC")
        mock_create.assert_called_with(id="1ABC", checked="2012-01-01 12:00:01")



class PdbFactoryTests(FactoryTest):

    @freeze_time("2012-01-01 12:00:01")
    @patch("zincbind.models.Pdb.objects.filter")
    @patch("zincbind.models.Pdb.objects.create")
    def test_can_create_pdb(self, mock_create, mock_filter):
        mock_filter.return_value = []
        mock_create.return_value = self.pdb_record
        pdb = create_pdb(self.pdb)
        mock_filter.assert_called_with(pk="1ABC")
        mock_create.assert_called_with(
         pk="1ABC", deposited=self.date, resolution=4.5,
         title="PDB TITLE.", checked="2012-01-01 12:00:01"
        )
        self.assertIs(pdb, self.pdb_record)


    @patch("zincbind.models.Pdb.objects.filter")
    @patch("zincbind.models.Pdb.objects.create")
    def test_can_create_existing_pdb(self, mock_create, mock_filter):
        pdb_record = Mock()
        mock_filter.return_value = [pdb_record]
        pdb = create_pdb(self.pdb)
        mock_filter.assert_called_with(pk="1ABC")
        self.assertIs(pdb, pdb_record)
        self.assertFalse(mock_create.called)



class ResidueFactoryTests(FactoryTest):

    @patch("zincbind.models.Residue.objects.filter")
    @patch("zincbind.models.Residue.objects.create")
    @patch("zincbind.models.Atom.objects.create")
    def test_can_create_residue(self, mock_atom, mock_res, mock_filter):
        mock_filter.return_value = []
        residue_record = Mock(name="resrec")
        mock_res.return_value = residue_record
        residue = create_residue(self.res1, self.pdb_record)
        mock_filter.assert_called_with(pk="1ABCB10")
        mock_res.assert_called_with(
         pk="1ABCB10", residue_id="B10", name="VAL",
         chain="C", number=21, pdb=self.pdb_record
        )
        mock_atom.assert_any_call(
         pk="1ABC1", atom_id=1, name="N2", x=15, y=16, z=17, element="N",
         charge=-1, bfactor=101, residue=residue_record
        )
        mock_atom.assert_any_call(
         pk="1ABC2", atom_id=2, name="Z5", x=25, y=26, z=27, element="Z",
         charge=-2, bfactor=202, residue=residue_record
        )
        self.assertIs(residue, residue_record)


    @patch("zincbind.models.Residue.objects.filter")
    @patch("zincbind.models.Residue.objects.create")
    @patch("zincbind.models.Atom.objects.create")
    def test_can_create_existing_residue(self, mock_atom, mock_res, mock_filter):
        residue_record = Mock()
        mock_filter.return_value = [residue_record]
        residue = create_residue(self.res1, self.pdb_record)
        self.assertFalse(mock_res.called)
        self.assertFalse(mock_atom.called)
        self.assertIs(residue, residue_record)



class ZincSiteFactoryTests(FactoryTest):

    @patch("zincbind.factories.create_pdb")
    @patch("zincbind.factories.create_residue")
    @patch("zincbind.models.ZincSite.objects.create")
    def test_can_create_zinc_site(self, mock_zinc, mock_res, mock_pdb):
        mock_pdb.return_value = self.pdb_record
        residue_record1, residue_record2 = Mock(), Mock()
        mock_res.side_effect = [residue_record1, residue_record2]
        residue_set = Mock()
        residue_set.add = MagicMock()
        site_record = Mock()
        mock_zinc.return_value = site_record
        site_record.residues = residue_set
        site = create_zinc_site(self.pdb, self.zinc, [self.res1, self.res2])
        mock_pdb.assert_called_with(self.pdb)
        mock_res.assert_any_call(self.res1, self.pdb_record)
        mock_res.assert_any_call(self.res2, self.pdb_record)
        mock_zinc.assert_called_with(pk="1ABCB505", x=15, y=16, z=17)
        self.assertIs(site, site_record)
        residue_set.add.assert_any_call(residue_record1)
        residue_set.add.assert_any_call(residue_record2)


    @patch("zincbind.factories.create_pdb")
    @patch("zincbind.factories.create_residue")
    @patch("zincbind.models.ZincSite.objects.create")
    def test_error_on_duplicate_zinc_sites(self, mock_zinc, mock_res, mock_pdb):
        mock_zinc.side_effect = IntegrityError()
        with self.assertRaises(DuplicateSiteError):
            create_zinc_site(self.pdb, self.zinc, [self.res1, self.res2])
