from zincdb.tests import UrlTest
from home import views

class HomeUrlTests(UrlTest):

    def test_home_page_url_resolves_to_home_page_view(self):
        self.check_url_returns_view("/", views.home_page)


    def test_about_page_url_resolves_to_about_page_view(self):
        self.check_url_returns_view("/about/", views.about_page)


    def test_changelog_page_url_resolves_to_changelog_page_view(self):
        self.check_url_returns_view("/changelog/", views.changelog_page)


    def test_auth_page_url_resolves_to_login_page_view(self):
        self.check_url_returns_view("/auth/", views.login_page)


    def test_logout_page_url_resolves_to_logout_page_view(self):
        self.check_url_returns_view("/logout/", views.logout_page)
