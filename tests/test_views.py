from unittest.mock import patch, Mock
from .base import ZincBindTest
from zincbind.views import *

class HomeViewTests(ZincBindTest):

    def test_home_view_uses_home_template(self):
        request = self.get_request("/")
        self.check_view_uses_template(home, request, "home.html")


    @patch("zincbind.views.ZincSite.objects.count")
    def test_home_view_gets_zinc_count(self, mock_count):
        mock_count.return_value = 20
        request = self.get_request("/")
        self.check_view_has_context(home, request, {"zinc_count": 20})


    @patch("zincbind.views.Pdb.objects.exclude")
    def test_home_view_gets_pdb_count(self, mock_exclude):
        resultset = Mock()
        mock_exclude.return_value = resultset
        resultset.count.return_value = 50
        request = self.get_request("/")
        self.check_view_has_context(home, request, {"pdb_count": 50})
        mock_exclude.assert_called_with(title=None)



class DataViewTests(ZincBindTest):

    def test_data_view_uses_data_template(self):
        request = self.get_request("/data/")
        self.check_view_uses_template(data, request, "data.html")


    @patch("zincbind.views.Pdb.objects.exclude")
    def test_home_view_gets_pdb_count(self, mock_exclude):
        resultset = Mock()
        mock_exclude.return_value = resultset
        resultset.count.return_value = 50
        request = self.get_request("/")
        self.check_view_has_context(data, request, {"pdb_with_zinc": 50})
        mock_exclude.assert_called_with(title=None)


    @patch("zincbind.views.Pdb.objects.filter")
    def test_home_view_gets_pdb_count(self, mock_filter):
        resultset = Mock()
        mock_filter.return_value = resultset
        resultset.count.return_value = 50
        request = self.get_request("/")
        self.check_view_has_context(data, request, {"pdb_without_zinc": 50})
        mock_filter.assert_called_with(title=None)
