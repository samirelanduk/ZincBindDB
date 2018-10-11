from unittest.mock import patch, Mock, MagicMock
from django.db.models import F
from django.http import Http404, QueryDict
from testarsenal import DjangoTest
from core.views import *

class HomeViewTests(DjangoTest):

    def setUp(self):
        self.patch1 = patch("core.views.Pdb.objects.count")
        self.mock_pdb_count = self.patch1.start()
        self.mock_pdb_count.return_value = 169
        self.patch2 = patch("core.views.ZincSite.objects.count")
        self.mock_zinc_count = self.patch2.start()
        self.mock_zinc_count.return_value = 120
        self.patch3 = patch("core.views.ZincSiteCluster.objects.count")
        self.mock_unique_zinc_count = self.patch3.start()
        self.mock_unique_zinc_count.return_value = 4


    def tearDown(self):
        self.patch1.stop()
        self.patch2.stop()
        self.patch3.stop()


    def test_home_view_uses_home_template(self):
        request = self.make_request("---")
        self.check_view_uses_template(home, request, "home.html")


    def test_home_view_sends_counts(self):
        request = self.make_request("---")
        self.check_view_has_context(home, request, {"counts": [4, 120, 169]})



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
        self.patch4 = patch("zinc.views.Pdb.blast_search")
        self.mock_blast = self.patch4.start()
        self.mock_blast.return_value = "BRESULTS"


    def tearDown(self):
        self.patch1.stop()
        self.patch2.stop()
        self.patch3.stop()
        self.patch4.stop()


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
         search, request, {"results": self.pag, "page": self.pag.page(), "chains": False}
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
         search, request, {"results": self.pag, "page": self.pag.page(), "chains": False}
        )
        self.pag.page.assert_called_with("3")


    def test_search_view_sends_blast_search_results_and_page(self):
        request = self.make_request("---", data={"sequence": "ABC"})
        self.check_view_has_context(
         search, request, {"results": self.pag, "page": self.pag.page()}
        )
        self.mock_blast.assert_called_with("ABC")
        self.mock_paginate.assert_called_with("BRESULTS", 25)
        self.pag.page.assert_called_with(1)
        request = self.make_request("---", data={"sequence": "ABC", "page": 3})
        self.check_view_has_context(
         search, request, {"results": self.pag, "page": self.pag.page(), "chains": True}
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




class AboutPageTests(DjangoTest):

    def test_about_view_uses_about_template(self):
        request = self.make_request("---")
        self.check_view_uses_template(about, request, "about.html")



class HelpPageTests(DjangoTest):

    def test_help_view_uses_help_template(self):
        request = self.make_request("---")
        self.check_view_uses_template(help, request, "help.html")



class DataPageTests(DjangoTest):

    def setUp(self):
        self.patch1 = patch("core.views.ZincSite.objects.all")
        self.mock_all_sites = self.patch1.start()
        self.patch2 = patch("core.views.Residue.name_counts")
        self.mock_names = self.patch2.start()
        self.patch3 = patch("core.views.ZincSite.property_counts")
        self.mock_properties = self.patch3.start()


    def tearDown(self):
        self.patch1.stop()
        self.patch2.stop()
        self.patch3.stop()


    def test_data_view_uses_data_template(self):
        request = self.make_request("---")
        self.check_view_uses_template(data, request, "data.html")


    def test_data_view_sends_correct_data(self):
        self.mock_names.return_value = "NAME DATA"
        self.mock_properties.side_effect = ["DATA1", "DATA2", "DATA3"]
        request = self.make_request("---")
        self.check_view_has_context(data, request, {"bar_data": [
         "NAME DATA", "DATA1", "DATA2", "DATA3"
        ]})
        self.mock_names.assert_called_with(5)
        self.mock_all_sites.return_value.annotate.assert_called_with(
         organism=F("pdb__organism"),
         classification=F("pdb__classification"),
         technique=F("pdb__technique")
        )
        sites = self.mock_all_sites.return_value.annotate.return_value
        self.mock_properties.assert_any_call(sites, "technique", 3)
        self.mock_properties.assert_any_call(sites, "classification", 6)
        self.mock_properties.assert_any_call(sites, "organism", 6)



class ChangelogPageTests(DjangoTest):

    def test_changelog_view_uses_changelog_template(self):
        request = self.make_request("---")
        self.check_view_uses_template(changelog, request, "changelog.html")
