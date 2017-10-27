from datetime import datetime
from django.test import TestCase
from django.core.urlresolvers import resolve

class ZincBindTest(TestCase):

    def setUp(self):
        self.date = datetime.now().date()


    def check_url_returns_view(self, url, view):
        resolver = resolve(url)
        self.assertEqual(resolver.func, view)
