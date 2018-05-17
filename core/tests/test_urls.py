from testarsenal import DjangoTest
import core.views as core_views
import zinc.views as zinc_views

class UrlTests(DjangoTest):

    def test_home_url(self):
        self.check_url_returns_view("/", core_views.home)


    def test_pdb_url(self):
        self.check_url_returns_view("/pdbs/a111/", zinc_views.pdb)
