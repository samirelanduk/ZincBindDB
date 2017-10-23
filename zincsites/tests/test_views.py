from datetime import datetime
from unittest.mock import Mock, patch
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from zincdb.tests import ViewTest
from zincsites.models import ZincSite, Pdb, Residue
from zincsites.views import *
from zincsites.exceptions import InvalidPdbError, DuplicateSiteError

class NewSiteViewTests(ViewTest):

    def setUp(self):
        ViewTest.setUp(self)
        self.data = {
         "pdb": "1TON", "zinc": "A247",
         "residue1": "A57", "residue2": "A97", "residue3": "A99"
        }
        self.creation_patcher = patch("zincsites.views.create_manual_zinc_site")
        self.mock_create = self.creation_patcher.start()



    def tearDown(self):
        self.creation_patcher.stop()


    def test_new_site_view_uses_new_site_template(self):
        request = self.get_user_request("/sites/new/")
        self.check_view_uses_template(new_site_page, request, "new-site.html")


    def test_new_site_view_is_protected(self):
        request = self.factory.get("/sites/new/")
        request.user = AnonymousUser()
        self.check_view_redirects(new_site_page, request, "/")


    def test_new_site_view_redirects_to_new_site_on_successful_post(self):
        request = self.get_user_request("/sites/new/", method="post", data=self.data)
        self.check_view_redirects(new_site_page, request, "/sites/1TONA247/")


    def test_new_site_view_creates_new_site(self):
        request = self.get_user_request("/sites/new/", method="post", data=self.data)
        new_site_page(request)
        self.mock_create.assert_called_with("1TON", "A247", ["A57", "A97", "A99"])


    def test_can_handle_missing_pdb(self):
        self.data["pdb"] = ""
        request = self.get_user_request("/sites/new/", method="post", data=self.data)
        self.check_view_uses_template(new_site_page, request, "new-site.html")
        self.check_view_has_context(
         new_site_page, request, {"error": "No PDB code supplied"}
        )


    def test_can_handle_invalid_pdb_format(self):
        self.mock_create.side_effect = InvalidPdbError()
        request = self.get_user_request("/sites/new/", method="post", data=self.data)
        self.check_view_uses_template(new_site_page, request, "new-site.html")
        self.check_view_has_context(
         new_site_page, request, {"error": "'1TON' is not a valid PDB"}
        )


    def test_can_handle_missing_zinc(self):
        self.data["zinc"] = ""
        request = self.get_user_request("/sites/new/", method="post", data=self.data)
        self.check_view_uses_template(new_site_page, request, "new-site.html")
        self.check_view_has_context(
         new_site_page, request, {"error": "No Zinc ID supplied"}
        )


    def test_can_handle_duplicate_zinc_site(self):
        self.mock_create.side_effect = DuplicateSiteError()
        request = self.get_user_request("/sites/new/", method="post", data=self.data)
        self.check_view_uses_template(new_site_page, request, "new-site.html")
        self.check_view_has_context(new_site_page, request, {
         "error": "There is already a zinc site called '1TONA247'"
        })


    def test_can_handle_invalid_zinc_site(self):
        self.mock_create.side_effect = NoSuchZincError()
        request = self.get_user_request("/sites/new/", method="post", data=self.data)
        self.check_view_uses_template(new_site_page, request, "new-site.html")
        self.check_view_has_context(new_site_page, request, {
         "error": "There is no Zinc with ID 'A247' in 1TON"
        })


    def test_can_handle_all_missing_residues(self):
        self.data["residue1"] = ""
        self.data["residue2"] = ""
        self.data["residue3"] = ""
        request = self.get_user_request("/sites/new/", method="post", data=self.data)
        self.check_view_uses_template(new_site_page, request, "new-site.html")
        self.check_view_has_context(
         new_site_page, request, {"error": "No Residue IDs supplied"}
        )


    def test_can_handle_invalid_residue(self):
        self.mock_create.side_effect = NoSuchResidueError("A999")
        request = self.get_user_request("/sites/new/", method="post", data=self.data)
        self.check_view_uses_template(new_site_page, request, "new-site.html")
        self.check_view_has_context(new_site_page, request, {
         "error": "There is no Residue with ID 'A999' in 1TON"
        })



class SiteViewTests(ViewTest):

    def setUp(self):
        ViewTest.setUp(self)
        self.get_patcher = patch("zincsites.views.ZincSite.objects.get")
        self.mock_get = self.get_patcher.start()


    def tearDown(self):
        self.get_patcher.stop()


    def test_site_view_uses_site_template(self):
        request = self.get_user_request("/sites/1XXXA500/")
        self.check_view_uses_template(site_page, request, "site.html", "1XXXA500")


    def test_site_view_sends_site(self):
        self.mock_get.return_value = "ZINCSITE"
        request = self.get_user_request("/sites/1XXXA500/")
        self.check_view_has_context(
         site_page, request, {"site": "ZINCSITE"}, "1XXXA500"
        )
        self.mock_get.assert_called_with(pk="1XXXA500")


    def test_404_on_incorrect_id(self):
        self.mock_get.side_effect = ObjectDoesNotExist()
        request = self.get_user_request("/sites/1XXXA500/")
        with self.assertRaises(Http404):
            response = site_page(request, "1XXXA500")


    '''def test_new_site_view_handles_invalid_pdb(self):
        self.mock_create.side_effect = InvalidPdbError
        response = self.client.post("/sites/new/", self.data)
        self.assertTemplateUsed(response, "new-site.html")
        self.assertIn("1TON", response.context["error_message"])
        self.assertIn("invalid", response.context["error_message"].lower())





    def test_new_site_view_handles_duplicate_zinc_site(self):
        self.mock_create.side_effect = DuplicateSiteError
        response = self.client.post("/sites/new/", self.data)
        self.assertTemplateUsed(response, "new-site.html")
        self.assertIn("already", response.context["error_message"].lower())


    def test_new_site_view_handles_invalid_zinc(self):
        self.mock_create.side_effect = NoSuchZincError
        response = self.client.post("/sites/new/", self.data)
        self.assertTemplateUsed(response, "new-site.html")
        self.assertIn("is no zinc", response.context["error_message"].lower())'''
