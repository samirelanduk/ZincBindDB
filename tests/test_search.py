from unittest.mock import patch, Mock, MagicMock
from .base import ZincBindTest
from zincbind.models import ZincSite
from zincbind.search import omni_search

class OmniSearchTests(ZincBindTest):

    @patch("zincbind.search.ZincSite.objects.filter")
    @patch("zincbind.search.Q")
    def test_can_search_properties(self, mock_q, mock_filter):
    	result_set = Mock()
    	result_set.order_by.return_value = ["r1", "r2", "r3"]
    	mock_filter.return_value = result_set
    	mock_q.side_effect = [1, 2, 3, 4, 5, 6]
    	results = omni_search("term")
    	mock_filter.assert_called_with(7)
    	result_set.order_by.assert_called_with("-pdb__deposited")
    	self.assertEqual(results, ["r1", "r2", "r3"])