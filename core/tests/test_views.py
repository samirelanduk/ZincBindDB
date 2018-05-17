from unittest.mock import patch, Mock, MagicMock
from testarsenal import DjangoTest
from core.views import *

class HomeViewTests(DjangoTest):

    def test_home_view_uses_home_template(self):
        request = self.make_request("---")
        self.check_view_uses_template(home, request, "home.html")
