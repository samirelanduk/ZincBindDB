from .base import ZincBindTest
from zincbind import views

class UrlRedirectTests(ZincBindTest):

    def test_home_url_works(self):
        self.check_url_returns_view("/", views.home)


    def test_data_url_works(self):
        self.check_url_returns_view("/data/", views.data)


    def test_search_url_works(self):
        self.check_url_returns_view("/search/", views.search)


    def test_site_url_works(self):
        self.check_url_returns_view("/1XXXA001/", views.site)
