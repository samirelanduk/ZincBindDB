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



class PdbViewTests(DjangoTest):

    def setUp(self):
        self.patch1 = patch("core.views.get_object_or_404")
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
        self.patch1 = patch("core.views.get_object_or_404")
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



class ChangelogPageTests(DjangoTest):

    def test_changelog_view_uses_changelog_template(self):
        request = self.make_request("---")
        self.check_view_uses_template(changelog, request, "changelog.html")
