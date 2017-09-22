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

    def test_login_view_uses_login_template(self):
        response = self.client.get("/auth/")
        self.assertTemplateUsed(response, "login.html")


    def test_login_view_redirects_to_home(self):
        response = self.client.post(
         "/auth/", data={"username": "testuser", "password": "testpassword"}
        )
        self.assertRedirects(response, "/")


    def test_login_view_can_login(self):
        self.client.logout()
        self.assertNotIn("_auth_user_id", self.client.session)
        response = self.client.post(
         "/auth/", data={"username": "testuser", "password": "testpassword"}
        )
        self.assertIn("_auth_user_id", self.client.session)


    def test_can_handle_incorrect_credentials(self):
        self.client.logout()
        self.assertNotIn("_auth_user_id", self.client.session)
        response = self.client.post(
         "/auth/", data={"username": "wrong", "password": "wrong"}
        )
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertTemplateUsed(response, "login.html")
        self.assertIn("incorrect", response.context["error"])



class LogoutViewTests(ViewTest):

    def test_logout_view_redirects_to_home(self):
        response = self.client.get("/logout/")
        self.assertRedirects(response, "/")


    def test_logout_view_logs_out(self):
        self.assertIn("_auth_user_id", self.client.session)
        response = self.client.get("/logout/")
        self.assertNotIn("_auth_user_id", self.client.session)
