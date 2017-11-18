from datetime import datetime
from unittest.mock import patch, Mock, MagicMock
from freezegun import freeze_time
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
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
        self.pdb.organism.return_value = "H SAP"
        self.pdb.expression_system.return_value = "M MUS"
        self.pdb.classification.return_value = "IG"
        self.pdb.technique.return_value = "XRAY"
        self.pdb.rfactor.return_value = 4.5
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
        self.atom1, self.atom2, self.atom3 = Mock(), Mock(), Mock()
        self.atom1.atom_id.return_value = 1
        self.atom1.x.return_value = 15
        self.atom1.y.return_value = 16
        self.atom1.z.return_value = 17
        self.atom1.element.return_value = "N"
        self.atom1.name.return_value = "N2"
        self.atom1.charge.return_value = -1
        self.atom1.bfactor.return_value = 101
        self.atom1.distance_to.return_value = 3.5
        self.atom2.atom_id.return_value = 2
        self.atom2.x.return_value = 25
        self.atom2.y.return_value = 26
        self.atom2.z.return_value = 27
        self.atom2.element.return_value = "C"
        self.atom2.name.return_value = "CA"
        self.atom2.charge.return_value = -2
        self.atom2.bfactor.return_value = 202
        self.atom2.distance_to.return_value = 4.5
        self.atom3.atom_id.return_value = 3
        self.atom3.x.return_value = 35
        self.atom3.y.return_value = 36
        self.atom3.z.return_value = 37
        self.atom3.element.return_value = "C"
        self.atom3.name.return_value = "CB"
        self.atom3.charge.return_value = -1
        self.atom3.bfactor.return_value = 20
        self.atom3.distance_to.return_value = 5.5
        self.res1.atoms.return_value = set([self.atom1, self.atom2, self.atom3])
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
    @patch("zincbind.models.Pdb.objects.get")
    @patch("zincbind.models.Pdb.objects.create")
    def test_can_create_pdb(self, mock_create, mock_get):
        mock_get.side_effect = ObjectDoesNotExist
        mock_create.return_value = self.pdb_record
        pdb = create_pdb(self.pdb)
        mock_get.assert_called_with(pk="1ABC")
        mock_create.assert_called_with(
         pk="1ABC", deposited=self.date, resolution=4.5,
         title="PDB TITLE.", rfactor=4.5, classification="IG",
         organism="H SAP", expression="M MUS", technique="XRAY",
         checked="2012-01-01 12:00:01"
        )
        self.assertIs(pdb, self.pdb_record)


    @patch("zincbind.models.Pdb.objects.get")
    @patch("zincbind.models.Pdb.objects.create")
    def test_can_create_existing_pdb(self, mock_create, mock_get):
        pdb_record = Mock()
        mock_get.return_value = pdb_record
        pdb = create_pdb(self.pdb)
        mock_get.assert_called_with(pk="1ABC")
        self.assertIs(pdb, pdb_record)
        self.assertFalse(mock_create.called)



class ResidueFactoryTests(FactoryTest):

    @patch("zincbind.models.Residue.objects.get")
    @patch("zincbind.models.Residue.objects.create")
    @patch("zincbind.models.Atom.objects.create")
    def test_can_create_residue(self, mock_atom, mock_res, mock_get):
        mock_get.side_effect = ObjectDoesNotExist
        residue_record = Mock(name="rec")
        mock_res.return_value = residue_record
        residue = create_residue(self.res1, "1ABC", "zincatom")
        mock_get.assert_called_with(pk="1ABCB10")
        mock_res.assert_called_with(
         pk="1ABCB10", residue_id="B10", name="VAL",
         chain="C", number=21
        )
        mock_atom.assert_any_call(
         pk="1ABC1", atom_id=1, name="N2", x=15, y=16, z=17, element="N",
         charge=-1, bfactor=101, alpha=False, beta=False, liganding=True,
         residue=residue_record
        )
        mock_atom.assert_any_call(
         pk="1ABC2", atom_id=2, name="CA", x=25, y=26, z=27, element="C",
         charge=-2, bfactor=202, alpha=True, beta=False, liganding=False,
         residue=residue_record
        )
        mock_atom.assert_any_call(
         pk="1ABC3", atom_id=3, name="CB", x=35, y=36, z=37, element="C",
         charge=-1, bfactor=20, alpha=False, beta=True, liganding=False,
         residue=residue_record
        )
        self.atom1.distance_to.assert_called_with("zincatom")
        self.atom2.distance_to.assert_called_with("zincatom")
        self.atom3.distance_to.assert_called_with("zincatom")
        self.assertIs(residue, residue_record)


    @patch("zincbind.models.Residue.objects.get")
    @patch("zincbind.models.Residue.objects.create")
    @patch("zincbind.models.Atom.objects.create")
    def test_can_create_existing_residue(self, mock_atom, mock_res, mock_get):
        residue_record = Mock()
        mock_get.return_value = residue_record
        residue = create_residue(self.res1, "1XXX", Mock())
        mock_get.assert_called_with(pk="1XXXB10")
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
        mock_res.assert_any_call(self.res1, "1ABC", self.atom1)
        mock_res.assert_any_call(self.res2, "1ABC", self.atom1)
        mock_zinc.assert_called_with(pk="1ABCB505", x=15, y=16, z=17, pdb=self.pdb_record)
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
