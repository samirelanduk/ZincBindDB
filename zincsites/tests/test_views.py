from datetime import datetime
from unittest.mock import Mock, patch
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from zincdb.tests import ViewTest
from zincsites.models import ZincSite, Pdb, Residue
from zincsites.views import *
from zincsites.exceptions import InvalidPdbError, DuplicateSiteError

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
        self.data["pdb"] = "1XXX"
        self.data["zinc"] = "A500"
        response = self.client.post("/sites/new/", data=self.data)
        self.assertRedirects(response, "/sites/1XXXA500/")


    def test_new_site_view_creates_new_site(self):
        self.mock_create.return_value = "SITE"
        response = self.client.post("/sites/new/", self.data)
        self.mock_create.assert_called_with("1TON", "A247", ["A57", "A97"])


    def test_new_site_view_handles_invalid_pdb(self):
        self.mock_create.side_effect = InvalidPdbError
        response = self.client.post("/sites/new/", self.data)
        self.assertTemplateUsed(response, "new-site.html")
        self.assertIn("1TON", response.context["error_message"])
        self.assertIn("invalid", response.context["error_message"].lower())


    def test_new_site_view_handles_missing_pdb(self):
        self.data["pdb"] = ""
        response = self.client.post("/sites/new/", self.data)
        self.assertTemplateUsed(response, "new-site.html")
        self.assertIn("didn't enter", response.context["error_message"].lower())


    def test_new_site_view_handles_duplicate_zinc_site(self):
        self.mock_create.side_effect = DuplicateSiteError
        response = self.client.post("/sites/new/", self.data)
        self.assertTemplateUsed(response, "new-site.html")
        self.assertIn("already", response.context["error_message"].lower())



class SiteViewTests(ViewTest):

    def test_site_view_uses_site_template(self):
        response = self.client.get("/sites/1XXXA500/")
        self.assertTemplateUsed(response, "site.html")


    def test_site_view_sends_site(self):
        response = self.client.get("/sites/1XXXA500/")
        self.assertEqual(
         response.context["site"],
         ZincSite.objects.get(id="1XXXA500")
        )


    def test_404_on_incorrect_id(self):
        response = self.client.get("/sites/1XXXA501/")
        self.assertEqual(response.status_code, 404)



class SiteCreationTests(ViewTest):

    @patch("zincsites.views.create_pdb")
    @patch("zincsites.views.create_residue")
    def test_can_create_site(self, mock_res, mock_pdb):
        pdb = Pdb.objects.get(id="1XXX")
        mock_res.side_effect = [Residue.objects.create(id="A{}".format(i * 10), number=i * 10, pdb=pdb) for i in range(2)]
        self.assertEqual(ZincSite.objects.all().count(), 1)
        mock_pdb.return_value = {"pdb": "dict"}
        site = create_site("1TON", "A247", ["A57", "A97"])
        mock_pdb.assert_called_with("1TON")
        mock_res.assert_any_call("A57", {"pdb": "dict"})
        mock_res.assert_any_call("A97", {"pdb": "dict"})
        self.assertEqual(ZincSite.objects.all().count(), 2)
        ZincSite.objects.first()
        self.assertEqual(ZincSite.objects.first().id, "1TONA247")
        self.assertEqual(ZincSite.objects.last().residues.count(), 2)
        self.assertEqual(site, ZincSite.objects.first())


    def test_can_warn_of_duplicate_site(self):
        with self.assertRaises(DuplicateSiteError):
            create_site("1XXX", "A500", ["A57", "A97"])



class PdbCreationTests(ViewTest):

    @patch("atomium.fetch_data")
    def test_can_create_pdb(self, mock_data):
        date = datetime(1985, 3, 1).date()
        mock_data.return_value = {"deposition_date": date, "title": "TTT"}
        self.assertEqual(Pdb.objects.all().count(), 1)
        pdb = create_pdb("1YYY")
        mock_data.assert_called_with("1YYY", pdbe=True)
        self.assertEqual(Pdb.objects.all().count(), 2)
        self.assertEqual(Pdb.objects.get(id="1YYY").id, "1YYY")
        self.assertEqual(Pdb.objects.get(id="1YYY").deposition_date, date)
        self.assertEqual(Pdb.objects.get(id="1YYY").title, "TTT")
        self.assertEqual(pdb, {"deposition_date": date, "title": "TTT"})


    @patch("atomium.fetch_data")
    def test_can_create_existing_pdb(self, mock_data):
        date = datetime(2000, 1, 1).date()
        mock_data.return_value = {"deposition_date": date, "title": "TTT"}
        self.assertEqual(Pdb.objects.all().count(), 1)
        pdb = create_pdb("1XXX")
        mock_data.assert_called_with("1XXX", pdbe=True)
        self.assertEqual(Pdb.objects.all().count(), 1)
        self.assertEqual(Pdb.objects.first().id, "1XXX")
        self.assertEqual(Pdb.objects.first().deposition_date, date)
        self.assertEqual(Pdb.objects.first().title, "TTT")
        self.assertEqual(pdb, {"deposition_date": date, "title": "TTT"})


    @patch("atomium.fetch_data")
    def test_can_handle_invalid_pdb(self, mock_data):
        mock_data.return_value = None
        self.assertEqual(Pdb.objects.all().count(), 1)
        with self.assertRaises(InvalidPdbError):
            pdb = create_pdb("1XXX")
        mock_data.assert_called_with("1XXX", pdbe=True)
        self.assertEqual(Pdb.objects.all().count(), 1)
        mock_data.side_effect = ValueError
        with self.assertRaises(InvalidPdbError):
            pdb = create_pdb("1XXX")



class ResidueCreationTests(ViewTest):

    def test_can_create_residue(self):
        Pdb.objects.create(id="1YYY", deposition_date=datetime.now().date(), title="VVV")
        self.assertEqual(Residue.objects.all().count(), 2)
        data = {"code": "1YYY", "models": [{"chains": [{"chain_id": "A", "residues": [
         {"id": "A12", "name": "TRP"}, {"id": "A13", "name": "VAL"}
        ]}]}]}
        residue = create_residue("A12", data)
        self.assertEqual(Residue.objects.all().count(), 3)
        self.assertEqual(Residue.objects.get(id="A12").id, "A12")
        self.assertEqual(Residue.objects.get(id="A12").number, 12)
        self.assertEqual(Residue.objects.get(id="A12").chain, "A")
        self.assertEqual(Residue.objects.get(id="A12").name, "TRP")
        self.assertEqual(Residue.objects.get(id="A12").pdb, Pdb.objects.get(pk="1YYY"))
        self.assertEqual(residue, Residue.objects.get(id="A12"))
