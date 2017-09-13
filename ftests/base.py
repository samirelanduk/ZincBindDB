from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User

class FunctionalTest(StaticLiveServerTestCase):

    def setUp(self):
        self.user = User.objects.create_user(
         username="testuser",
         password="testpassword"
        )
        self.browser = webdriver.Chrome()


    def tearDown(self):
        self.browser.quit()


    def login(self):
        self.client.login(username="testuser", password="testpassword")
        cookie = self.client.cookies["sessionid"].value
        self.browser.get(self.live_server_url + "/")
        self.browser.add_cookie({
         "name": "sessionid", "value": cookie, "secure": False, "path": "/"
        })
        self.browser.refresh()


    def get(self, url):
        self.browser.get(self.live_server_url + url)


    def check_page(self, url):
        self.assertEqual(self.browser.current_url, self.live_server_url + url)
