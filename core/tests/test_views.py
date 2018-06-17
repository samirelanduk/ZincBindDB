from unittest.mock import patch, Mock, MagicMock
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
        self.patch3 = patch("core.views.ZincSite.objects.values_list")
        self.mock_unique_zinc_count = self.patch3.start()
        self.mock_unique_zinc_count.return_value = [1, 2, 1, 4, 3, 2, 1]


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
        self.mock_unique_zinc_count.assert_called_with("cluster", flat=True)



class AboutPageTests(DjangoTest):

    def test_about_view_uses_about_template(self):
        request = self.make_request("---")
        self.check_view_uses_template(about, request, "about.html")



class DataPageTests(DjangoTest):

    def test_data_view_uses_data_template(self):
        request = self.make_request("---")
        self.check_view_uses_template(data, request, "data.html")



class ChangelogPageTests(DjangoTest):

    def test_changelog_view_uses_changelog_template(self):
        request = self.make_request("---")
        self.check_view_uses_template(changelog, request, "changelog.html")
