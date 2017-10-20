from unittest.mock import patch, Mock, MagicMock
from zincdb.tests import FactoryTest
from zincsites.factories import create_pdb, create_zinc_site, create_residue

class PdbFactoryTests(FactoryTest):

    @patch("zincsites.models.Pdb.objects.filter")
    @patch("zincsites.models.Pdb.objects.create")
    def test_can_create_pdb(self, mock_create, mock_filter):
        mock_filter.return_value = []
        mock_create.return_value = self.pdb_record
        pdb = create_pdb(self.pdb)
        mock_filter.assert_called_with(pk="1ABC")
        mock_create.assert_called_with(
         pk="1ABC", deposition_date=self.date, title="PDB TITLE."
        )
        self.assertIs(pdb, self.pdb_record)


    @patch("zincsites.models.Pdb.objects.filter")
    @patch("zincsites.models.Pdb.objects.create")
    def test_can_create_existing_pdb(self, mock_create, mock_filter):
        pdb_record = Mock()
        mock_filter.return_value = [pdb_record]
        pdb = create_pdb(self.pdb)
        mock_filter.assert_called_with(pk="1ABC")
        self.assertIs(pdb, pdb_record)
        self.assertFalse(mock_create.called)



class ZincSiteFactoryTests(FactoryTest):

    @patch("zincsites.factories.create_pdb")
    @patch("zincsites.factories.create_residue")
    @patch("zincsites.models.ZincSite.objects.create")
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
        mock_zinc.assert_called_with(pk="1ABCB505")
        self.assertIs(site, site_record)
        residue_set.add.assert_any_call(residue_record1)
        residue_set.add.assert_any_call(residue_record2)



class ResidueFactoryTests(FactoryTest):

    @patch("zincsites.models.Residue.objects.filter")
    @patch("zincsites.models.Residue.objects.create")
    @patch("zincsites.models.Atom.objects.create")
    def test_can_create_residue(self, mock_atom, mock_res, mock_filter):
        mock_filter.return_value = []
        residue_record = Mock(name="resrec")
        mock_res.return_value = residue_record
        residue = create_residue(self.res1, self.pdb_record)
        mock_filter.assert_called_with(pk="1ABCB10")
        mock_res.assert_called_with(
         pk="1ABCB10", residue_id="B10", number=21, chain="C", pdb=self.pdb_record
        )
        mock_atom.assert_any_call(
         pk="1ABC1", atom_id=1, x=15, y=16, z=17, element="N", name="N2",
         charge=-1, bfactor=101, residue=residue_record
        )
        mock_atom.assert_any_call(
         pk="1ABC2", atom_id=2, x=25, y=26, z=27, element="Z", name="Z5",
         charge=-2, bfactor=202, residue=residue_record
        )
        self.assertIs(residue, residue_record)


    @patch("zincsites.models.Residue.objects.filter")
    @patch("zincsites.models.Residue.objects.create")
    @patch("zincsites.models.Atom.objects.create")
    def test_can_create_existing_residue(self, mock_atom, mock_res, mock_filter):
        residue_record = Mock()
        mock_filter.return_value = [residue_record]
        residue = create_residue(self.res1, self.pdb_record)
        self.assertFalse(mock_res.called)
        self.assertFalse(mock_atom.called)
        self.assertIs(residue, residue_record)
