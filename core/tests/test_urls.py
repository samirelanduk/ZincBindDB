from testarsenal import DjangoTest
import core.views as core_views
import zinc.views as zinc_views

class UrlTests(DjangoTest):

    def test_home_url(self):
        self.check_url_returns_view("/", core_views.home)


    def test_search_url(self):
        self.check_url_returns_view("/search", zinc_views.search)


    def test_pdb_url(self):
        self.check_url_returns_view("/pdbs/a111/", zinc_views.pdb)


    def test_zinc_site_url(self):
        self.check_url_returns_view("/a1113456/", zinc_views.zinc_site)
