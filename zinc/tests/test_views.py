from unittest.mock import patch, Mock, MagicMock
from testarsenal import DjangoTest
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


    def tearDown(self):
        self.patch1.stop()
        self.patch2.stop()


    def test_search_view_uses_search_template(self):
        request = self.make_request("---", data={"q": "X"})
        self.check_view_uses_template(search, request, "search.html")


    def test_search_view_sends_search_results_and_page(self):
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
