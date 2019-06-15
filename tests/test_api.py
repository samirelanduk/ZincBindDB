import kirjava
from django.test import LiveServerTestCase

class ApiTest(LiveServerTestCase):

    fixtures = ["post-cluster.json"]

    def setUp(self):
        self.client = kirjava.Client(self.live_server_url)
        self.client.headers["Accept"] = "application/json"
        self.client.headers["Content-Type"] = "application/json"



class PdbApiTests(ApiTest):

    def test_can_get_pdb(self):
        data = self.client.execute("""{pdb(id: "1XDA") {
         id title organism expressionSystem keywords classification
         assembly resolution rvalue depositionDate technique skeleton
        }}""")
        self.assertEqual(data, {"data": {"pdb": {
         "id": "1XDA", "title": "STRUCTURE OF INSULIN", "organism": "Homo sapiens",
         "expressionSystem": "Saccharomyces cerevisiae",  "skeleton": False,
         "keywords": "HORMONE, METABOLIC ROLE, CHEMICAL ACTIVITY, INSULIN ALBUMIN, FATTY ACID, GLUCOSE METABOLISM, DIABETES",
         "classification": "HORMONE", "assembly": 5, "resolution": 1.8, "rvalue": 0.174,
         "depositionDate": "1996-12-18", "technique": "X-RAY DIFFRACTION"}}})
    

    def test_can_get_all_pdbs(self):
        data = self.client.execute("""{pdbs { count edges { node { id }}} }""")
        self.assertEqual(data, {"data": {"pdbs": {"count": 10, "edges": [
         {"node": {"id": "12CA"}}, {"node": {"id": "1BNT"}}, {"node": {"id": "1DEH"}},
         {"node": {"id": "1G48"}}, {"node": {"id": "1IZB"}}, {"node": {"id": "1MSO"}},
         {"node": {"id": "1XDA"}}, {"node": {"id": "3HUD"}}, {"node": {"id": "5Y5B"}},
         {"node": {"id": "6ISO"}}
        ]}}})
    

    def test_can_filter_pdbs(self):
        data = self.client.execute("""{pdbs(title__contains: "insulin", sort: "title") {
         count edges { node { id title }}
        }}""")
        self.assertEqual(data, {"data": {"pdbs": {"count": 3, "edges": [
         {"node": {"id": "1IZB", "title": "ROLE OF B13 GLU IN INSULIN ASSEMBLY: THE HEXAMER STRUCTURE OF RECOMBINANT MUTANT (B13 GLU-> GLN) INSULIN"}},
         {"node": {"id": "1XDA", "title": "STRUCTURE OF INSULIN"}},
         {"node": {"id": "1MSO", "title": "T6 Human Insulin at 1.0 A Resolution"}}
        ]}}})
        