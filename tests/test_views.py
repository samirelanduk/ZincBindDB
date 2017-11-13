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
        request = self.get_request("/search/", "get", {"term": "TERM"})
        self.check_view_uses_template(search, request, "search.html")


    def test_search_view_redirects_if_no_term(self):
        request = self.get_request("/search/", "get")
        self.check_view_redirects(search, request, "/")


    def test_search_view_sends_search_term(self):
        request = self.get_request("/search/", "get", {"term": "TERM"})
        self.check_view_has_context(search, request, {"term": "TERM"})


    @patch("zincbind.views.omni_search")
    def test_search_view_sends_search_results(self, mock_omni):
        mock_omni.return_value = ["RESULT1", "RESULT2"]
        request = self.get_request("/search/", "get", {"term": "TERM"})
        self.check_view_has_context(search, request, {
         "results": ["RESULT1", "RESULT2"], "result_count": 2
        })


    @patch("zincbind.views.omni_search")
    def test_search_view_sends_search_results_first_25(self, mock_omni):
        mock_omni.return_value = list(range(130))
        request = self.get_request("/search/", "get", {"term": "TERM"})
        self.check_view_has_context(search, request, {
         "results": list(range(25)), "result_count": 130
        })


    @patch("zincbind.views.omni_search")
    def test_search_view_searches_sends_pagination_details_one_page(self, mock_omni):
        mock_omni.return_value = ["RESULT1", "RESULT2"]
        request = self.get_request("/search/", "get", {"term": "TERM"})
        self.check_view_has_context(search, request, {
         "page_count": 1, "page": 1, "previous": False, "next": False
        })


    @patch("zincbind.views.omni_search")
    def test_search_view_searches_sends_pagination_details_multi_page(self, mock_omni):
        mock_omni.return_value = list(range(130))
        request = self.get_request("/search/", "get", {"term": "TERM"})
        self.check_view_has_context(search, request, {
         "page_count": 6, "page": 1, "previous": False, "next": 2
        })


    @patch("zincbind.views.omni_search")
    def test_search_view_handles_second_25(self, mock_omni):
        mock_omni.return_value = list(range(130))
        request = self.get_request("/search/", "get", {"term": "TERM", "page": 2})
        self.check_view_has_context(search, request, {
         "results": list(range(25, 50)), "result_count": 130,
         "page_count": 6, "page": 2, "previous": 1, "next": 3
        })


    @patch("zincbind.views.omni_search")
    def test_search_view_handles_last_results(self, mock_omni):
        mock_omni.return_value = list(range(130))
        request = self.get_request("/search/", "get", {"term": "TERM", "page": 6})
        self.check_view_has_context(search, request, {
         "results": list(range(125, 130)), "result_count": 130,
         "page_count": 6, "page": 6, "previous": 5, "next": False
        })


    @patch("zincbind.views.omni_search")
    def test_search_view_handles_invalid_page(self, mock_omni):
        mock_omni.return_value = list(range(130))
        request = self.get_request("/search/", "get", {"term": "TERM", "page": "ghgh"})
        self.check_view_has_context(search, request, {
         "results": list(range(25)), "result_count": 130,
         "page_count": 6, "page": 1, "previous": False, "next": 2
        })
        request = self.get_request("/search/", "get", {"term": "TERM", "page": -1})
        self.check_view_has_context(search, request, {
         "results": list(range(25)), "result_count": 130,
         "page_count": 6, "page": 1, "previous": False, "next": 2
        })
        request = self.get_request("/search/", "get", {"term": "TERM", "page": 30})
        self.check_view_has_context(search, request, {
         "results": list(range(25)), "result_count": 130,
         "page_count": 6, "page": 1, "previous": False, "next": 2
        })



class SiteViewTests(ZincBindTest):

    def setUp(self):
        ZincBindTest.setUp(self)
        self.get_patcher = patch("zincbind.views.ZincSite.objects.get")
        self.mock_get = self.get_patcher.start()


    def tearDown(self):
        self.get_patcher.stop()


    def test_site_view_uses_site_template(self):
        request = self.get_request("/somesite/")
        self.check_view_uses_template(site, request, "site.html", "ID")


    def test_site_view_sends_site(self):
        self.mock_get.return_value = "ZINCSITE"
        request = self.get_request("/somesite/")
        self.check_view_has_context(
         site, request, {"site": "ZINCSITE"}, "siteid"
        )
        self.mock_get.assert_called_with(pk="siteid")
