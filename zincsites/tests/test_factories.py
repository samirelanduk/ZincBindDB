from unittest.mock import patch, Mock, MagicMock
from zincdb.tests import FactoryTest
from zincsites.factories import create_pdb

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
