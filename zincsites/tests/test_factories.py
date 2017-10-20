from unittest.mock import patch, Mock, MagicMock
from zincdb.tests import FactoryTest
from zincsites.factories import create_pdb, create_zinc_site

class PdbFactoryTests(FactoryTest):

    @patch("zincsites.models.Pdb.objects.filter")
    @patch("zincsites.models.Pdb.objects.create")
    def test_can_create_pdb(self, mock_create, mock_filter):
        pdb_record = Mock()
        mock_filter.return_value = []
        mock_create.return_value = pdb_record
        pdb = create_pdb(self.pdb)
        mock_filter.assert_called_with(pk="1ABC")
        mock_create.assert_called_with(
         pk="1ABC", deposition_date=self.date, title="PDB TITLE."
        )
        self.assertIs(pdb, pdb_record)


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
        pdb_record = Mock()
        pdb_record.id = "1ABC"
        mock_pdb.return_value = pdb_record
        residue_record1, residue_record2 = Mock(), Mock()
        mock_res.side_effect = [residue_record1, residue_record2]
        residue_set = Mock()
        residue_set.add = MagicMock()
        site_record = Mock())
        mock_zinc.return_value = site_record
        site_record.residues = residue_set
        site = create_zinc_site(self.pdb, self.zinc, [self.res1, self.res2])
        mock_pdb.assert_called_with(self.pdb)
        mock_res.assert_any_call(self.res1, pdb_record)
        mock_res.assert_any_call(self.res2, pdb_record)
        mock_zinc.assert_called_with(pk="1ABCB505")
        self.assertIs(site, site_record)
        residue_set.add.assert_any_call(residue_record1)
        residue_set.add.assert_any_call(residue_record2)
