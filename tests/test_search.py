from unittest.mock import patch, Mock, MagicMock
from .base import ZincBindTest
from zincbind.models import ZincSite
from zincbind.search import omni_search

class OmniSearchTests(ZincBindTest):

    @patch("zincbind.models.ZincSite.objects.filter")
    def test_can_search_zinc_ids(self, mock_filter):
        mock_filter.return_value = ["r1", "r2", "r3"]
        results = omni_search("term")
        mock_filter.assert_called_with(id__contains="TERM")
        self.assertEqual(results, ["r1", "r2", "r3"])
