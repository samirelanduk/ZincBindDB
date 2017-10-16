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
        pdb = Pdb.objects.create(id="1XXX", deposition_date="2000-01-01", title="TTT")
        res1 = Residue.objects.create(id="A1", number=1, name="VAL", chain="A", pdb=pdb)
        res2 = Residue.objects.create(id="A2", number=2, name="TYR", chain="A", pdb=pdb)
        site = ZincSite.objects.create(id="1XXXA500")
        site.residues.add(res1)
        site.residues.add(res2)



class UrlTest(ZincDbTest):

    def check_url_returns_view(self, url, view):
        resolver = resolve(url)
        self.assertEqual(resolver.func, view)



class ViewTest(ZincDbTest):
    pass



class ModelTest(ZincDbTest):
    pass
