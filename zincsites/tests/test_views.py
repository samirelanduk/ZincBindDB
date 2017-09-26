from zincdb.tests import ViewTest

class NewSiteViewTests(ViewTest):

    def test_new_site_view_uses_new_site_template(self):
        response = self.client.get("/sites/new/")
        self.assertTemplateUsed(response, "new-site.html")


    def test_new_site_view_is_protected(self):
        self.client.logout()
        response = self.client.get("/sites/new/")
        self.assertRedirects(response, "/")


    def test_new_site_view_redirects_to_new_site_on_successful_post(self):
        response = self.client.post("/sites/new/", data={
         "pdb": "1TON", "zinc": "A247", "residue1": "A57", "residue2": "A97"
        })
        self.assertRedirects(response, "/sites/1TONA247/")



class SiteViewTests(ViewTest):

    def test_new_site_view_uses_new_site_template(self):
        response = self.client.get("/sites/1XXXB123/")
        self.assertTemplateUsed(response, "site.html")
