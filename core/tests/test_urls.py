from testarsenal import DjangoTest
import core.views as core_views

class UrlTests(DjangoTest):

    def test_home_url(self):
        self.check_url_returns_view("/", core_views.home)


    def test_data_url(self):
        self.check_url_returns_view("/data/", core_views.data)


    def test_about_url(self):
        self.check_url_returns_view("/about/", core_views.about)


    def test_help_url(self):
        self.check_url_returns_view("/help/", core_views.help)


    def test_changelog_url(self):
        self.check_url_returns_view("/changelog/", core_views.changelog)


    def test_search_url(self):
        self.check_url_returns_view("/search", core_views.search)
        self.check_url_returns_view("/search/", core_views.search)


    def test_pdb_url(self):
        self.check_url_returns_view("/pdbs/a111/", core_views.pdb)


    def test_zinc_site_url(self):
        self.check_url_returns_view("/a1113456/", core_views.zinc_site)
