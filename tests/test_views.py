from .base import ZincBindTest
from zincbind.views import *

class HomeViewTests(ZincBindTest):

    def test_home_view_uses_home_template(self):
        request = self.get_request("/")
        self.check_view_uses_template(home, request, "home.html")
