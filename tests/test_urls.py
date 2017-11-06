from .base import ZincBindTest
from zincbind import views

class UrlRedirectTests(ZincBindTest):

    def test_home_url_works(self):
        self.check_url_returns_view("/", views.home)


    def test_data_url_works(self):
        self.check_url_returns_view("/data/", views.data)
