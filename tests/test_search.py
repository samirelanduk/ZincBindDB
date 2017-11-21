from unittest.mock import patch, Mock, MagicMock
from .base import ZincBindTest
from zincbind.models import ZincSite
from zincbind.search import omni_search

class OmniSearchTests(ZincBindTest):

    @patch("zincbind.models.ZincSite.objects.filter")
    def test_can_search_zinc_ids(self, mock_filter):
    	result_set = Mock()
    	result_set.order_by.return_value = ["r1", "r2", "r3"]
    	mock_filter.return_value = result_set
    	results = omni_search("term")
    	mock_filter.assert_called_with(id__contains="TERM")
    	result_set.order_by.assert_called_with("-pdb__deposited")