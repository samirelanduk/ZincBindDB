from unittest.mock import patch, Mock, MagicMock
from testarsenal import DjangoTest
from django.http import Http404, QueryDict
from zinc.views import *

class SearchViewTests(DjangoTest):

    def setUp(self):
        self.patch1 = patch("zinc.views.Pdb.search")
        self.mock_search = self.patch1.start()
        self.mock_search.return_value = "RESULTS"
        self.patch2 = patch("zinc.views.Paginator")
        self.mock_paginate = self.patch2.start()
        self.pag = Mock()
        self.mock_paginate.return_value = self.pag
        self.patch3 = patch("zinc.views.Pdb.advanced_search")
        self.mock_advanced = self.patch3.start()
        self.mock_advanced.return_value = "!RESULTS"


    def tearDown(self):
        self.patch1.stop()
        self.patch2.stop()
        self.patch3.stop()


    def test_search_view_uses_template_with_no_search_terms(self):
        request = self.make_request("---")
        self.check_view_uses_template(search, request, "advanced-search.html")


    def test_search_view_uses_search_template(self):
        request = self.make_request("---", data={"q": "X"})
        self.check_view_uses_template(search, request, "search-results.html")


    def test_search_view_sends_simple_search_results_and_page(self):
        request = self.make_request("---", data={"q": "X"})
        self.check_view_has_context(
         search, request, {"results": self.pag, "page": self.pag.page()}
        )
        self.mock_search.assert_called_with("X")
        self.mock_paginate.assert_called_with("RESULTS", 25)
        self.pag.page.assert_called_with(1)
        request = self.make_request("---", data={"q": "X", "page": 3})
        self.check_view_has_context(
         search, request, {"results": self.pag, "page": self.pag.page()}
        )
        self.pag.page.assert_called_with("3")


    def test_search_view_sends_advanced_search_results_and_page(self):
        request = self.make_request("---", data={"title": "X"})
        self.check_view_has_context(
         search, request, {"results": self.pag, "page": self.pag.page()}
        )
        self.mock_advanced.assert_called_with(QueryDict("title=X"))
        self.mock_paginate.assert_called_with("!RESULTS", 25)
        self.pag.page.assert_called_with(1)
        request = self.make_request("---", data={"title": "X", "page": 3})
        self.check_view_has_context(
         search, request, {"results": self.pag, "page": self.pag.page()}
        )
        self.pag.page.assert_called_with("3")


    def test_can_raise_404_on_invalid_page_number(self):
        request = self.make_request("---", data={"q": "X", "page": 100})
        self.pag.page.side_effect = Exception
        with self.assertRaises(Http404):
            search(request)



class PdbViewTests(DjangoTest):

    def setUp(self):
        self.patch1 = patch("zinc.views.get_object_or_404")
        self.mock_get = self.patch1.start()
        self.pdb = Mock()
        self.mock_get.return_value = self.pdb


    def tearDown(self):
        self.patch1.stop()


    def test_pdb_view_uses_pdb_template(self):
        request = self.make_request("---")
        self.check_view_uses_template(pdb, request, "pdb.html", "AXXX")


    def test_pdb_view_sends_pdb(self):
        request = self.make_request("---")
        self.check_view_has_context(pdb, request, {"pdb": self.pdb}, "AXXX")
        self.mock_get.assert_called_with(Pdb, id="AXXX")



class ZincSiteViewTests(DjangoTest):

    def setUp(self):
        self.patch1 = patch("zinc.views.get_object_or_404")
        self.mock_get = self.patch1.start()
        self.site = Mock()
        self.mock_get.return_value = self.site


    def tearDown(self):
        self.patch1.stop()


    def test_zinc_site_view_uses_zinc_site_template(self):
        request = self.make_request("---")
        self.check_view_uses_template(zinc_site, request, "zinc-site.html", "AXXX4")


    def test_zinc_site_view_sends_zinc_site(self):
        request = self.make_request("---")
        self.check_view_has_context(zinc_site, request, {"site": self.site}, "AXXX4")
        self.mock_get.assert_called_with(ZincSite, id="AXXX4")
