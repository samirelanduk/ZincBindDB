from unittest.mock import patch, Mock, MagicMock
from django.db.models import F
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
