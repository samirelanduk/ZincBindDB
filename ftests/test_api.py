from .base import FunctionalTest
import requests

class APIRetrievalTests(FunctionalTest):

    def test_can_get_pdb(self):
        pdb = requests.get(self.live_server_url + "/api/pdbs/6EQU/").json()
        self.assertEqual(pdb["id"], "6EQU")
        self.assertEqual(pdb["classification"], "LYASE")
