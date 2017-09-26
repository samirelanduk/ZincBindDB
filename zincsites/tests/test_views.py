from unittest.mock import Mock, patch
from zincdb.tests import ViewTest
from zincsites.models import ZincSite
from zincsites.views import create_site

class NewSiteViewTests(ViewTest):

    def setUp(self):
        ViewTest.setUp(self)
        self.creation_patcher = patch("zincsites.views.create_site")
        self.mock_create = self.creation_patcher.start()
        self.data = {
         "pdb": "1TON", "zinc": "A247",
         "residue1": "A57", "residue2": "A97", "residue3": ""
        }


    def tearDown(self):
        self.creation_patcher.stop()


    def test_new_site_view_uses_new_site_template(self):
        response = self.client.get("/sites/new/")
        self.assertTemplateUsed(response, "new-site.html")


    def test_new_site_view_is_protected(self):
        self.client.logout()
        response = self.client.get("/sites/new/")
        self.assertRedirects(response, "/")


    def test_new_site_view_redirects_to_new_site_on_successful_post(self):
        self.mock_create.side_effect = lambda a,b,c: ZincSite.objects.create(id="1TONA247")
        response = self.client.post("/sites/new/", data=self.data)
        self.assertRedirects(response, "/sites/1TONA247/")


    def test_new_site_view_creates_new_site(self):
        response = self.client.post("/sites/new/", self.data)
        self.mock_create.assert_called_with("1TON", "A247", ["A57", "A97"])



class SiteViewTests(ViewTest):

    def setUp(self):
        self.site = ZincSite.objects.create(id="1XXXB123")


    def test_site_view_uses_site_template(self):
        response = self.client.get("/sites/1XXXB123/")
        self.assertTemplateUsed(response, "site.html")


    def test_site_view_sends_site(self):
        response = self.client.get("/sites/1XXXB123/")
        self.assertEqual(response.context["site"], self.site)


    def test_404_on_incorrect_id(self):
        response = self.client.get("/sites/1XXXB124/")
        self.assertEqual(response.status_code, 404)



class SiteCreationTests(ViewTest):

    def test_can_create_site(self):
        self.assertEqual(ZincSite.objects.all().count(), 0)
        create_site("1TON", "A247", ["A57", "A97"])
        self.assertEqual(ZincSite.objects.all().count(), 1)
        site = ZincSite.objects.first()
        self.assertEqual(site.id, "1TONA247")
