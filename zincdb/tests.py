from django.core.urlresolvers import resolve
from django.contrib.auth.models import User
from django.test import TestCase

class ZincDbTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
         username="testuser",
         password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")



class UrlTest(ZincDbTest):

    def check_url_returns_view(self, url, view):
        resolver = resolve(url)
        self.assertEqual(resolver.func, view)



class ViewTest(ZincDbTest):
    pass



class ModelTest(ZincDbTest):
    pass
