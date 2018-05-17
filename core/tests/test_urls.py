from testarsenal import DjangoTest
import core.views as core_views

class UrlTests(DjangoTest):

    def test_home_url(self):
        self.check_url_returns_view("/", core_views.home)
