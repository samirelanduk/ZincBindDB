from datetime import datetime
from unittest.mock import Mock, patch
from zincdb.tests import ViewTest
from zincsites.models import ZincSite, Pdb, Residue
from zincsites.views import create_site, create_pdb, create_residue

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
        self.mock_create.return_value = "SITE"
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

    @patch("zincsites.views.create_pdb")
    @patch("zincsites.views.create_residue")
    def test_can_create_site(self, mock_res, mock_pdb):
        pdb = Pdb.objects.create(id="1XXX", deposition_date=datetime.now().date(), title="T")
        mock_res.side_effect = [Residue.objects.create(id="A{}".format(i), pdb=pdb) for i in range(2)]
        self.assertEqual(ZincSite.objects.all().count(), 0)
        mock_pdb.return_value = {"pdb": "dict"}
        site = create_site("1TON", "A247", ["A57", "A97"])
        mock_pdb.assert_called_with("1TON")
        mock_res.assert_any_call("A57", {"pdb": "dict"})
        mock_res.assert_any_call("A97", {"pdb": "dict"})
        self.assertEqual(ZincSite.objects.all().count(), 1)
        ZincSite.objects.first()
        self.assertEqual(ZincSite.objects.first().id, "1TONA247")
        self.assertEqual(ZincSite.objects.first().residues.count(), 2)
        self.assertEqual(site, ZincSite.objects.first())



class PdbCreationTests(ViewTest):

    @patch("atomium.fetch_data")
    def test_can_create_pdb(self, mock_data):
        date = datetime(1985, 3, 1).date()
        mock_data.return_value = {"deposition_date": date, "title": "TTT"}
        self.assertEqual(Pdb.objects.all().count(), 0)
        pdb = create_pdb("1XXX")
        mock_data.assert_called_with("1XXX", pdbe=True)
        self.assertEqual(Pdb.objects.all().count(), 1)
        self.assertEqual(Pdb.objects.first().id, "1XXX")
        self.assertEqual(Pdb.objects.first().deposition_date, date)
        self.assertEqual(Pdb.objects.first().title, "TTT")
        self.assertEqual(pdb, {"deposition_date": date, "title": "TTT"})



class ResidueCreationTests(ViewTest):

    def test_can_create_residue(self):
        Pdb.objects.create(id="1XXX", deposition_date=datetime.now().date(), title="TTT")
        Pdb.objects.create(id="1YYY", deposition_date=datetime.now().date(), title="VVV")
        self.assertEqual(Residue.objects.all().count(), 0)
        data = {"code": "1YYY", "models": [{"chains": [{"chain_id": "A", "residues": [
         {"id": "A12", "name": "TRP"}, {"id": "A13", "name": "VAL"}
        ]}]}]}
        residue = create_residue("A12", data)
        self.assertEqual(Residue.objects.all().count(), 1)
        self.assertEqual(Residue.objects.first().id, "A12")
        self.assertEqual(Residue.objects.first().chain, "A")
        self.assertEqual(Residue.objects.first().name, "TRP")
        self.assertEqual(Residue.objects.first().pdb, Pdb.objects.get(pk="1YYY"))
        self.assertEqual(residue, Residue.objects.first())
