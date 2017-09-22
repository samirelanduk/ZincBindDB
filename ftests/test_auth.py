from time import sleep
from .base import FunctionalTest

class LoginTests(FunctionalTest):

    def test_can_login(self):
        # User goes to login page
        self.get("/auth/")
        self.check_title("Log In")
        self.check_h1("Log In")

        # There is a login form
        form = self.browser.find_element_by_tag_name("form")
        username, password = form.find_elements_by_tag_name("input")[:2]
        submit = form.find_elements_by_tag_name("input")[-1]

        # The user logs in
        username.send_keys("testuser")
        password.send_keys("testpassword")
        submit.click()

        # They are on the home page
        self.check_page("/")

        # They are logged in
        nav_links = self.browser.find_element_by_id("nav-links")
        nav_links = nav_links.find_elements_by_tag_name("a")
        self.assertEqual(nav_links[-1].text, "Log Out")


    def test_cant_login_with_wrong_information(self):
        # User goes to login page
        self.get("/auth/")
        self.check_title("Log In")
        self.check_h1("Log In")

        # There is a login form
        form = self.browser.find_element_by_tag_name("form")
        username, password = form.find_elements_by_tag_name("input")[:2]
        submit = form.find_elements_by_tag_name("input")[-1]

        # The user tries to log in
        username.send_keys("testuser")
        password.send_keys("testpasswordx")
        submit.click()

        # They are still on the auth page
        self.check_page("/auth/")

        # There is an error message
        form = self.browser.find_element_by_tag_name("form")
        error_message = form.find_element_by_id("error-message")
        self.assertIn("incorrect", error_message.text)
