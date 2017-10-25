from zincdb.tests import UrlTest
from zincsites import views

class SitesUrlTests(UrlTest):

    def test_new_site_urls_resolves_to_new_site_view(self):
        self.check_url_returns_view("/sites/new/", views.new_site_page)


    def test_site_urls_resolves_to_site_view(self):
        self.check_url_returns_view("/sites/1XXXB123/", views.site_page)


    def test_sites_urls_resolves_to_sites_view(self):
        self.check_url_returns_view("/sites/", views.sites_page)
