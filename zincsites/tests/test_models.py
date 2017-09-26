from django.core.exceptions import ValidationError
from unittest.mock import patch
from zincdb.tests import ModelTest
from zincsites.models import ZincSite

class ZincSiteTests(ModelTest):

    def test_save_and_retrieve_zinc_sites(self):
        self.assertEqual(ZincSite.objects.all().count(), 0)
        site = ZincSite(id="1XXXA999")
        site.save()
        self.assertEqual(ZincSite.objects.all().count(), 1)
        retrieved_site = ZincSite.objects.first()
        self.assertEqual(retrieved_site, site)
