from datetime import datetime
from unittest.mock import Mock
from django.core.urlresolvers import resolve
from django.contrib.auth.models import User
from django.test import TransactionTestCase, RequestFactory
from zincsites.models import *

class ZincDbTest(TransactionTestCase):

    def setUp(self):
        self.user = User.objects.create_user(
         username="testuser",
         password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")
        self.date = datetime(2010, 1, 1).date()



class UrlTest(ZincDbTest):

    def check_url_returns_view(self, url, view):
        resolver = resolve(url)
        self.assertEqual(resolver.func, view)



class ViewTest(ZincDbTest):
    pass



class ModelTest(ZincDbTest):
    pass



class FactoryTest(ZincDbTest):

    def setUp(self):
        ZincDbTest.setUp(self)
        self.pdb = Mock()
        self.pdb.code.return_value = "1ABC"
        self.pdb.deposition_date.return_value = self.date
        self.pdb.title.return_value = "PDB TITLE."
        self.zinc = Mock()
        self.zinc.molecule_id.return_value = "B505"
        self.res1 = Mock()
        self.res2 = Mock()
