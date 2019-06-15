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



class ZincSiteApiTests(ApiTest):
    
    def test_can_get_zincsite(self):
        data = self.client.execute("""{zincsite(id: "1XDA-1") {
         id family residueNames representative
        }}""")
        self.assertEqual(data, {"data": {"zincsite": {
         "id": "1XDA-1", "family": "H3", "residueNames": ".CL..HIS.", "representative": False
        }}})
    

    def test_can_get_all_zincsites(self):
        data = self.client.execute("""{zincsites { count edges { node { id }}} }""")
        self.assertEqual(data, {"data": {"zincsites": {"count": 19, "edges": [
         {"node": {"id": "12CA-1"}}, {"node": {"id": "1BNT-1"}}, {"node": {"id": "1DEH-1"}},
         {"node": {"id": "1DEH-2"}}, {"node": {"id": "1DEH-3"}}, {"node": {"id": "1DEH-4"}},
         {"node": {"id": "1G48-1"}}, {"node": {"id": "1IZB-1"}}, {"node": {"id": "1IZB-2"}},
         {"node": {"id": "1MSO-1"}}, {"node": {"id": "1MSO-2"}}, {"node": {"id": "1XDA-1"}},
         {"node": {"id": "1XDA-2"}}, {"node": {"id": "3HUD-1"}}, {"node": {"id": "3HUD-2"}},
         {"node": {"id": "3HUD-3"}}, {"node": {"id": "3HUD-4"}}, {"node": {"id": "5Y5B-1"}},
         {"node": {"id": "6ISO-1"}}
        ]}}})
    

    def test_can_filter_zincsites(self):
        data = self.client.execute("""{zincsites(residueNames__contains: ".HIS.", representative: true) { count edges { node { id }}} }""")
        self.assertEqual(data, {"data": {"zincsites": {"count": 4, "edges": [
         {"node": {"id": "12CA-1"}}, {"node": {"id": "1IZB-1"}}, {"node": {"id": "3HUD-2"}},
         {"node": {"id": "5Y5B-1"}}
        ]}}})
    

    def test_can_get_pdb_zincsite(self):
        data = self.client.execute("""{pdb(id: "1XDA") {zincsite(id: "1XDA-1") {
         id family residueNames representative
        }}}""")
        self.assertEqual(data, {"data": {"pdb": {"zincsite": {
         "id": "1XDA-1", "family": "H3", "residueNames": ".CL..HIS.", "representative": False
        }}}})
    

    def test_can_get_all_pdb_zincsites(self):
        data = self.client.execute("""{pdb(id: "1XDA") {zincsites { count edges { node { id }}}}}""")
        self.assertEqual(data, {"data": {"pdb": {"zincsites": {"count": 2, "edges": [
         {"node": {"id": "1XDA-1"}}, {"node": {"id": "1XDA-2"}}
        ]}}}})



class MetalApiTests(ApiTest):
    
    def test_can_get_metal(self):
        data = self.client.execute("""{metal(id: 1) {
         id atomiumId name x y z element residueName residueNumber insertionCode
         chainId omissionReason
        }}""")
        self.assertEqual(data, {"data": {"metal": {
         "id": "1", "atomiumId": 2028, "name": "ZN", "x": -6.677, "y": -1.626,
         "z": 15.471, "element": "ZN", "residueName": "ZN", "residueNumber": 262,
         "insertionCode": "", "chainId": "A", "omissionReason": None
        }}})
    

    def test_can_get_all_metals(self):
        data = self.client.execute("""{metals { count edges { node { id }}} }""")
        self.assertEqual(data, {"data": {"metals": {"count": 26, "edges": [
         {"node": {"id": "1"}}, {"node": {"id": "2"}}, {"node": {"id": "3"}},
         {"node": {"id": "4"}}, {"node": {"id": "5"}}, {"node": {"id": "6"}},
         {"node": {"id": "7"}}, {"node": {"id": "8"}}, {"node": {"id": "9"}},
         {"node": {"id": "10"}}, {"node": {"id": "11"}}, {"node": {"id": "12"}},
         {"node": {"id": "13"}}, {"node": {"id": "14"}}, {"node": {"id": "15"}},
         {"node": {"id": "16"}}, {"node": {"id": "17"}}, {"node": {"id": "18"}},
         {"node": {"id": "19"}}, {"node": {"id": "20"}}, {"node": {"id": "21"}},
         {"node": {"id": "22"}}, {"node": {"id": "23"}}, {"node": {"id": "24"}},
         {"node": {"id": "25"}}, {"node": {"id": "26"}}
        ]}}})
    

    def test_can_filter_metals(self):
        data = self.client.execute("""{metals(omissionReason__contains: "") { count edges { node { id omissionReason }}} }""")
        self.assertEqual(data, {"data": {"metals": {"count": 6, "edges": [
         {"node": {"id": "6", "omissionReason": "Zinc in asymmetric unit but not biological assembly."}},
         {"node": {"id": "7", "omissionReason": "Zinc in asymmetric unit but not biological assembly."}},
         {"node": {"id": "20", "omissionReason": "Zinc in asymmetric unit but not biological assembly."}},
         {"node": {"id": "21", "omissionReason": "Zinc in asymmetric unit but not biological assembly."}},
         {"node": {"id": "22", "omissionReason": "Zinc in asymmetric unit but not biological assembly."}},
         {"node": {"id": "23", "omissionReason": "Zinc in asymmetric unit but not biological assembly."}}
        ]}}})
    

    def test_can_get_pdb_metal(self):
        data = self.client.execute("""{pdb(id: "12CA") {metal(id: 1) {
         id atomiumId name x y z element residueName residueNumber insertionCode
         chainId omissionReason
        }}}""")
        self.assertEqual(data, {"data": {"pdb": {"metal": {
         "id": "1", "atomiumId": 2028, "name": "ZN", "x": -6.677, "y": -1.626,
         "z": 15.471, "element": "ZN", "residueName": "ZN", "residueNumber": 262,
         "insertionCode": "", "chainId": "A", "omissionReason": None
        }}}})
    

    def test_can_get_all_pdb_metals(self):
        data = self.client.execute("""{pdb(id: "12CA") {metals { count edges { node { id }}}}}""")
        self.assertEqual(data, {"data": {"pdb": {"metals": {"count": 1, "edges": [
         {"node": {"id": "1"}} 
        ]}}}})
    

    def test_can_get_zincsite_metal(self):
        data = self.client.execute("""{zincsite(id: "12CA-1") {metal(id: 1) {
         id atomiumId name x y z element residueName residueNumber insertionCode
         chainId omissionReason
        }}}""")
        self.assertEqual(data, {"data": {"zincsite": {"metal": {
         "id": "1", "atomiumId": 2028, "name": "ZN", "x": -6.677, "y": -1.626,
         "z": 15.471, "element": "ZN", "residueName": "ZN", "residueNumber": 262,
         "insertionCode": "", "chainId": "A", "omissionReason": None
        }}}})
    

    def test_can_get_all_zincsite_metals(self):
        data = self.client.execute("""{zincsite(id: "12CA-1") {metals { count edges { node { id }}}}}""")
        self.assertEqual(data, {"data": {"zincsite": {"metals": {"count": 1, "edges": [
         {"node": {"id": "1"}} 
        ]}}}})