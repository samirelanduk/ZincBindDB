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



class SearchViewTests(ZincBindTest):

    def test_search_view_uses_search_template(self):
        request = self.get_request("/search/", "post", {"term": "TERM"})
        self.check_view_uses_template(search, request, "search.html")


    def test_search_view_sends_search_term(self):
        request = self.get_request("/search/", "post", {"term": "TERM"})
        self.check_view_has_context(search, request, {"term": "TERM"})


    @patch("zincbind.views.omni_search")
    def test_search_view_searches(self, mock_omni):
        mock_omni.return_value = ["RESULT1", "RESULT2"]
        request = self.get_request("/search/", "post", {"term": "TERM"})
        self.check_view_has_context(
         search, request, {"results": ["RESULT1", "RESULT2"]}
        )



class SiteViewTests(ZincBindTest):

    def test_site_view_uses_site_template(self):
        request = self.get_request("/somesite/")
        self.check_view_uses_template(site, request, "site.html", "ID")
