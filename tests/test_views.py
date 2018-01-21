from unittest.mock import patch, Mock, MagicMock
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
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
    def test_data_view_gets_pdb_count(self, mock_exclude):
        resultset = Mock()
        mock_exclude.return_value = resultset
        resultset.count.return_value = 50
        request = self.get_request("/")
        self.check_view_has_context(data, request, {"pdb_with_zinc": 50})
        mock_exclude.assert_called_with(title=None)


    @patch("zincbind.views.Pdb.objects.filter")
    def test_data_view_gets_negative_pdb_count(self, mock_filter):
        resultset = Mock()
        mock_filter.return_value = resultset
        resultset.count.return_value = 50
        request = self.get_request("/")
        self.check_view_has_context(data, request, {"pdb_without_zinc": 50})
        mock_filter.assert_called_with(title=None)


    @patch("zincbind.views.Residue.objects.values_list")
    def test_data_view_gets_residue_frequencies(self, mock_values):
        mock_values.return_value = list("AAAAAAAABBBBBBBCCCCCCDDDDDEEEEFFFGGHIJK")
        request = self.get_request("/")
        self.check_view_has_context(data, request, {"residue_frequencies": [
         ["A", "B", "C", "D", "E", "F", "G", "Other"],
         [8, 7, 6, 5, 4, 3, 2, 4]
        ]})
        mock_values.assert_called_with("name", flat=True)


    @patch("zincbind.views.ZincSite.objects.values_list")
    def test_data_view_gets_species_frequencies(self, mock_values):
        mock_values.return_value = list("AAAAAAAABBBBBBBCCCCCCDDDDDEEEEFFFGGHIJK")
        request = self.get_request("/")
        self.check_view_has_context(data, request, {"species_frequencies": [
         ["A", "B", "C", "D", "E", "F", "G", "Other"],
         [8, 7, 6, 5, 4, 3, 2, 4]
        ]})
        mock_values.assert_called_with("pdb__organism", flat=True)



class SearchViewTests(ZincBindTest):

    @patch("zincbind.views.advanced_search")
    def test_no_params_uses_advanced_search(self, mock_view):
        mock_view.return_value = "RESPONSE"
        request = self.get_request("/search/", "get")
        response = search(request)
        mock_view.assert_called_with(request)
        self.assertEqual(response, "RESPONSE")


    @patch("zincbind.views.process_search")
    def test_params_uses_process_search(self, mock_view):
        mock_view.return_value = "RESPONSE"
        request = self.get_request("/search/", "get", {"term": "*"})
        response = search(request)
        mock_view.assert_called_with(request)
        self.assertEqual(response, "RESPONSE")



class ProcessSearchTests(ZincBindTest):

    def test_process_search_view_uses_search_template(self):
        request = self.get_request("/search/", "get", {"term": "TERM"})
        self.check_view_uses_template(process_search, request, "search.html")


    def test_process_search_view_sends_search_term(self):
        request = self.get_request("/search/", "get", {"term": "TERM"})
        self.check_view_has_context(process_search, request, {"term": "TERM"})


    @patch("zincbind.views.omni_search")
    def test_process_search_view_sends_search_results(self, mock_omni):
        mock_omni.return_value = ["RESULT1", "RESULT2"]
        request = self.get_request("/search/", "get", {"term": "TERM"})
        self.check_view_has_context(process_search, request, {
         "results": ["RESULT1", "RESULT2"], "result_count": 2
        })


    @patch("zincbind.views.omni_search")
    def test_process_search_view_sends_search_results_first_25(self, mock_omni):
        mock_omni.return_value = list(range(130))
        request = self.get_request("/search/", "get", {"term": "TERM"})
        self.check_view_has_context(process_search, request, {
         "results": list(range(25)), "result_count": 130
        })


    @patch("zincbind.views.omni_search")
    def test_process_search_view_searches_sends_pagination_details_one_page(self, mock_omni):
        mock_omni.return_value = ["RESULT1", "RESULT2"]
        request = self.get_request("/search/", "get", {"term": "TERM"})
        self.check_view_has_context(process_search, request, {
         "page_count": 1, "page": 1, "previous": False, "next": False, "url": "/search?term=TERM"
        })


    @patch("zincbind.views.omni_search")
    def test_process_search_view_searches_sends_pagination_details_multi_page(self, mock_omni):
        mock_omni.return_value = list(range(130))
        request = self.get_request("/search/", "get", {"term": "TERM"})
        self.check_view_has_context(process_search, request, {
         "page_count": 6, "page": 1, "previous": False, "next": 2, "url": "/search?term=TERM"
        })


    @patch("zincbind.views.omni_search")
    def test_process_search_view_handles_second_25(self, mock_omni):
        mock_omni.return_value = list(range(130))
        request = self.get_request("/search/", "get", {"term": "TERM", "page": 2})
        self.check_view_has_context(process_search, request, {
         "results": list(range(25, 50)), "result_count": 130,
         "page_count": 6, "page": 2, "previous": 1, "next": 3, "url": "/search?term=TERM"
        })


    @patch("zincbind.views.omni_search")
    def test_process_search_view_handles_last_results(self, mock_omni):
        mock_omni.return_value = list(range(130))
        request = self.get_request("/search/", "get", {"term": "TERM", "page": 6})
        self.check_view_has_context(process_search, request, {
         "results": list(range(125, 130)), "result_count": 130,
         "page_count": 6, "page": 6, "previous": 5, "next": False, "url": "/search?term=TERM"
        })


    @patch("zincbind.views.omni_search")
    def test_process_search_view_handles_invalid_page(self, mock_omni):
        mock_omni.return_value = list(range(130))
        request = self.get_request("/search/", "get", {"term": "TERM", "page": "ghgh"})
        self.check_view_has_context(process_search, request, {
         "results": list(range(25)), "result_count": 130,
         "page_count": 6, "page": 1, "previous": False, "next": 2, "url": "/search?term=TERM"
        })
        request = self.get_request("/search/", "get", {"term": "TERM", "page": -1})
        self.check_view_has_context(process_search, request, {
         "results": list(range(25)), "result_count": 130,
         "page_count": 6, "page": 1, "previous": False, "next": 2, "url": "/search?term=TERM"
        })
        request = self.get_request("/search/", "get", {"term": "TERM", "page": 30})
        self.check_view_has_context(process_search, request, {
         "results": list(range(25)), "result_count": 130,
         "page_count": 6, "page": 1, "previous": False, "next": 2, "url": "/search?term=TERM"
        })


    @patch("zincbind.views.omni_search")
    def test_process_search_view_can_get_all_results(self, mock_omni):
        mock_omni.return_value = ["RESULT1", "RESULT2"]
        request = self.get_request("/search/", "get", {"term": "*"})
        self.check_view_has_context(process_search, request, {
         "results": ["RESULT1", "RESULT2"], "result_count": 2, "url": "/search?term=*"
        })
        mock_omni.assert_called_with("")


    @patch("zincbind.views.specific_search")
    def test_can_use_specific_search_if_no_term(self, mock_specific):
        mock_specific.return_value = ["RESULT1", "RESULT2"]
        request = self.get_request("/search/", "get", {"x": "*", "y": "x z"})
        self.check_view_has_context(process_search, request, {
         "results": ["RESULT1", "RESULT2"], "result_count": 2, "url": "/search?x=*&y=x+z"
        })
        mock_specific.assert_called_with(x=["*"], y=["x z"])



class AdvancedSearchTests(ZincBindTest):

    def test_advanced_search_uses_advanced_search_template(self):
        request = self.get_request("/search/")
        self.check_view_uses_template(advanced_search, request, "advanced-search.html")



class SiteViewTests(ZincBindTest):

    def setUp(self):
        ZincBindTest.setUp(self)
        self.get_patcher = patch("zincbind.views.ZincSite.objects.get")
        self.filter_patcher = patch("zincbind.views.ZincSite.objects.filter")
        self.mock_get = self.get_patcher.start()
        self.mock_filter = self.filter_patcher.start()


    def tearDown(self):
        self.get_patcher.stop()
        self.mock_filter.stop()


    def test_site_view_uses_site_template(self):
        request = self.get_request("/somesite/")
        self.check_view_uses_template(site, request, "site.html", "ID")


    def test_site_view_sends_site(self):
        mock_site = Mock()
        mock_site.pdb = Mock()
        self.mock_get.return_value = mock_site
        request = self.get_request("/somesite/")
        self.check_view_has_context(
         site, request, {"site":mock_site}, "siteid"
        )
        self.mock_get.assert_called_with(pk="siteid")


    def test_site_view_sends_pdb_sites(self):
        filtered = Mock()
        self.mock_filter.side_effect = [filtered, Mock()]
        filtered.exclude.return_value = ["1", "2", "3"]
        mock_site = Mock()
        self.mock_get.return_value = mock_site
        mock_site.id = "ID"
        request = self.get_request("/somesite/")
        self.check_view_has_context(
         site, request, {"pdb_sites": ["1", "2", "3"]}, "siteid"
        )
        self.mock_filter.assert_any_call(pdb=mock_site.pdb)
        filtered.exclude.assert_any_call(id="ID")


    def test_site_view_sends_class_sites(self):
        filtered = Mock()
        self.mock_filter.side_effect = [Mock(), filtered]
        excluded = Mock()
        filtered.exclude.return_value = excluded
        excluded.order_by.return_value = ["1", "2", "3"]
        mock_site = Mock()
        self.mock_get.return_value = mock_site
        mock_site.id = "ID"
        request = self.get_request("/somesite/")
        self.check_view_has_context(
         site, request, {"class_sites": ["1", "2", "3"]}, "siteid"
        )
        self.mock_filter.assert_any_call(pdb=mock_site.pdb)
        filtered.exclude.assert_any_call(id="ID")
        excluded.order_by.assert_called_with("-pdb__deposited")


    def test_404_on_unknown_site(self):
        self.mock_get.side_effect = ObjectDoesNotExist()
        request = self.get_request("/sites/1XXXA500/")
        with self.assertRaises(Http404):
            site(request, "1XXXA500")



class ChangelogViewTests(ZincBindTest):

    def test_changelog_view_uses_changelog_template(self):
        request = self.get_request("/changelog/")
        self.check_view_uses_template(changelog, request, "changelog.html")
