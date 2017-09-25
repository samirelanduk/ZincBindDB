from zincdb.tests import ViewTest

class NewSiteViewTests(ViewTest):

    def test_new_site_view_uses_new_site_template(self):
        response = self.client.get("/sites/new/")
        self.assertTemplateUsed(response, "new-site.html")


    def test_new_site_view_is_protected(self):
        self.client.logout()
        response = self.client.get("/sites/new/")
        self.assertRedirects(response, "/")
