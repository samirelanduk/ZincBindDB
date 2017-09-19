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
