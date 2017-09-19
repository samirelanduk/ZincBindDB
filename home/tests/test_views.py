from zincdb.tests import ViewTest

class HomePageViewTests(ViewTest):

    def test_home_view_uses_home_template(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "home.html")



class AboutPageViewTests(ViewTest):

    def test_about_view_uses_about_template(self):
        response = self.client.get("/about/")
        self.assertTemplateUsed(response, "about.html")



class HelpPageViewTests(ViewTest):

    def test_help_view_uses_help_template(self):
        response = self.client.get("/help/")
        self.assertTemplateUsed(response, "help.html")



class ChangelogPageViewTests(ViewTest):

    def test_changelog_view_uses_changelog_template(self):
        response = self.client.get("/changelog/")
        self.assertTemplateUsed(response, "changelog.html")



class LoginPageViewTests(ViewTest):

    def test_changelog_view_uses_changelog_template(self):
        response = self.client.get("/auth/")
        self.assertTemplateUsed(response, "login.html")
