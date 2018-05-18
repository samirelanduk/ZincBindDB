from unittest.mock import patch, Mock, MagicMock
from testarsenal import DjangoTest
from zinc.views import *

class PdbViewTests(DjangoTest):

    def setUp(self):
        self.patch1 = patch("zinc.views.get_object_or_404")
        self.mock_get = self.patch1.start()
        self.pdb = Mock()
        self.mock_get.return_value = self.pdb


    def tearDown(self):
        self.patch1.stop()


    def test_pdb_view_uses_pdb_template(self):
        request = self.make_request("---")
        self.check_view_uses_template(pdb, request, "pdb.html", "AXXX")


    def test_pdb_view_sends_pdb(self):
        request = self.make_request("---")
        self.check_view_has_context(pdb, request, {"pdb": self.pdb}, "AXXX")
        self.mock_get.assert_called_with(Pdb, id="AXXX")
