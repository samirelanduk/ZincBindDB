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



class ResidueApiTests(ApiTest):
    
    def test_can_get_residue(self):
        data = self.client.execute("""{residue(id: 1) {
         id residueNumber insertionCode name atomiumId chainIdentifier
         chainSignature
        }}""")
        self.assertEqual(data, {"data": {"residue": {
         "id": "1", "residueNumber": 119, "insertionCode": "", "name": "HIS",
         "atomiumId": "A.119", "chainIdentifier": "A", "chainSignature": "leu.HIS.leu"
        }}})
    

    def test_can_get_all_residues(self):
        data = self.client.execute("""{residues { count edges { node {id }}}}""")
        self.assertEqual(data, {"data": {"residues": {"count": 83, "edges": [
         {"node": {"id": "12"}}, {"node": {"id": "13"}}, {"node": {"id": "14"}},
         {"node": {"id": "18"}}, {"node": {"id": "19"}}, {"node": {"id": "20"}},
         {"node": {"id": "24"}}, {"node": {"id": "25"}}, {"node": {"id": "26"}},
         {"node": {"id": "28"}}, {"node": {"id": "29"}}, {"node": {"id": "30"}},
         {"node": {"id": "32"}}, {"node": {"id": "33"}}, {"node": {"id": "34"}},
         {"node": {"id": "38"}}, {"node": {"id": "39"}}, {"node": {"id": "40"}},
         {"node": {"id": "27"}}, {"node": {"id": "31"}}, {"node": {"id": "47"}},
         {"node": {"id": "55"}}, {"node": {"id": "62"}}, {"node": {"id": "69"}},
         {"node": {"id": "48"}}, {"node": {"id": "56"}}, {"node": {"id": "63"}},
         {"node": {"id": "70"}}, {"node": {"id": "81"}}, {"node": {"id": "82"}},
         {"node": {"id": "83"}}, {"node": {"id": "2"}}, {"node": {"id": "6"}},
         {"node": {"id": "10"}}, {"node": {"id": "3"}}, {"node": {"id": "7"}},
         {"node": {"id": "11"}}, {"node": {"id": "44"}}, {"node": {"id": "52"}},
         {"node": {"id": "60"}}, {"node": {"id": "67"}}, {"node": {"id": "41"}},
         {"node": {"id": "49"}}, {"node": {"id": "57"}}, {"node": {"id": "64"}},
         {"node": {"id": "42"}}, {"node": {"id": "50"}}, {"node": {"id": "58"}},
         {"node": {"id": "65"}}, {"node": {"id": "35"}}, {"node": {"id": "36"}},
         {"node": {"id": "37"}}, {"node": {"id": "43"}}, {"node": {"id": "51"}},
         {"node": {"id": "59"}}, {"node": {"id": "66"}}, {"node": {"id": "1"}},
         {"node": {"id": "4"}}, {"node": {"id": "8"}}, {"node": {"id": "75"}},
         {"node": {"id": "76"}}, {"node": {"id": "45"}}, {"node": {"id": "53"}},
         {"node": {"id": "61"}}, {"node": {"id": "68"}}, {"node": {"id": "77"}},
         {"node": {"id": "71"}}, {"node": {"id": "72"}}, {"node": {"id": "73"}},
         {"node": {"id": "78"}}, {"node": {"id": "46"}}, {"node": {"id": "54"}},
         {"node": {"id": "79"}}, {"node": {"id": "15"}}, {"node": {"id": "16"}},
         {"node": {"id": "17"}}, {"node": {"id": "21"}}, {"node": {"id": "22"}},
         {"node": {"id": "23"}}, {"node": {"id": "74"}}, {"node": {"id": "80"}},
         {"node": {"id": "5"}}, {"node": {"id": "9"}}
        ]}}})
    

    def test_can_filter_residues(self):
        data = self.client.execute("""{residues(residueNumber__gt: 400) { count edges { node {atomiumId residueNumber}}}}""")
        self.assertEqual(data, {"data": {"residues": {"count": 11, "edges": [
         {"node": {"atomiumId": "A.425", "residueNumber": 425}},
         {"node": {"atomiumId": "B.511", "residueNumber": 511}},
         {"node": {"atomiumId": "B.511", "residueNumber": 511}},
         {"node": {"atomiumId": "B.511", "residueNumber": 511}},
         {"node": {"atomiumId": "D.512", "residueNumber": 512}},
         {"node": {"atomiumId": "D.512", "residueNumber": 512}},
         {"node": {"atomiumId": "D.512", "residueNumber": 512}},
         {"node": {"atomiumId": "A.531", "residueNumber": 531}},
         {"node": {"atomiumId": "A.551", "residueNumber": 551}},
         {"node": {"atomiumId": "A.555", "residueNumber": 555}},
         {"node": {"atomiumId": "A.555", "residueNumber": 555}}
        ]}}})
    

    def test_can_get_zincsite_residue(self):
        data = self.client.execute("""{zincsite(id: "12CA-1") {residue(id: 1) {
         id residueNumber insertionCode name atomiumId chainIdentifier
         chainSignature
        }}}""")
        self.assertEqual(data, {"data": {"zincsite": {"residue": {
         "id": "1", "residueNumber": 119, "insertionCode": "", "name": "HIS",
         "atomiumId": "A.119", "chainIdentifier": "A", "chainSignature": "leu.HIS.leu"
        }}}})
    

    def test_can_get_zincsite_all_residues(self):
        data = self.client.execute("""{zincsite(id: "12CA-1") {residues { edges { node {
         name atomiumId
        }}}}}""")
        self.assertEqual(data, {"data": {"zincsite": {"residues": {"edges": [
         {"node": {"name": "HIS", "atomiumId": "A.94"}},
         {"node": {"name": "HIS", "atomiumId": "A.96"}},
         {"node": {"name": "HIS", "atomiumId": "A.119"}}
        ]}}}})



class AtomApiTests(ApiTest):
    
    def test_can_get_atom(self):
        data = self.client.execute("""{atom(id: 1) {
         id atomiumId name x y z element 
        }}""")
        self.assertEqual(data, {"data": {"atom": {
         "id": "1", "atomiumId": 914, "name": "N", "x": -12.014, "y": -2.627, "z": 14.976, "element": "N" 
        }}})
    

    def test_can_get_all_atoms(self):
        data = self.client.execute("""{atoms { count }}""")
        self.assertEqual(data, {"data": {"atoms": {"count": 645}}})
    

    def test_can_filter_atoms(self):
        data = self.client.execute("""{atoms(element: "CL") { count edges { node { x y z}}}}""")
        self.assertEqual(data, {"data": {"atoms": {"count": 2, "edges": [
         {"node": {"x": 0.0, "y": 0.0, "z": 56.498}},
         {"node": {"x": 0.0, "y": 0.0, "z": 76.191}}
        ]}}})
    

    def test_can_get_residue_atom(self):
        data = self.client.execute("""{residue(id: 1) {atom(id: 1) {
         id atomiumId name x y z element 
        }}}""")
        self.assertEqual(data, {"data": {"residue": {"atom": {
         "id": "1", "atomiumId": 914, "name": "N", "x": -12.014, "y": -2.627, "z": 14.976, "element": "N" 
        }}}})
    

    def test_can_get_residue_atoms(self):
        data = self.client.execute("""{residue(id: 1) {atoms { count edges { node {
         atomiumId name 
        }}}}}""")
        self.assertEqual(data, {"data": {"residue": {"atoms": {"count": 10, "edges": [
         {"node": {"atomiumId": 914, "name": "N"}}, {"node": {"atomiumId": 915, "name": "CA"}},
         {"node": {"atomiumId": 916, "name": "C"}}, {"node": {"atomiumId": 917, "name": "O"}},
         {"node": {"atomiumId": 918, "name": "CB"}}, {"node": {"atomiumId": 919, "name": "CG"}},
         {"node": {"atomiumId": 920, "name": "ND1"}}, {"node": {"atomiumId": 921, "name": "CD2"}},
         {"node": {"atomiumId": 922, "name": "CE1"}}, {"node": {"atomiumId": 923, "name": "NE2"}}
        ]}}}})



class CoordinateBondApiTests(ApiTest):
    
    def test_can_get_coordinate_bond(self):
        data = self.client.execute("""{coordinateBond(id: 1) {
         id atom { id } metal { id }
        }}""")
        self.assertEqual(data, {"data": {"coordinateBond": {
         "id": "1", "atom": {"id": "20"}, "metal": {"id": "1"}
        }}})
    

    def test_can_get_coordinate_bonds(self):
        data = self.client.execute("""{coordinateBonds { count }}""")
        self.assertEqual(data, {"data": {"coordinateBonds": {"count": 85}}})
    

    def test_can_get_atom_coordinate_bond(self):
        data = self.client.execute("""{atom(id: 20) {
         coordinateBond(id: 1) { id metal { id }}
        }}""")
        self.assertEqual(data, {
         "data": {"atom": {"coordinateBond": {"id": "1", "metal": {"id": "1"}}}}
        })
    

    def test_can_get_atom_coordinate_bonds(self):
        data = self.client.execute("""{atom(id: 20) {
         coordinateBonds { edges { node { id metal { id }}}}
        }}""")
        self.assertEqual(data, {
         "data": {"atom": {"coordinateBonds": {"edges": [
          {"node": {"id": "1", "metal": {"id": "1"}}}
         ]}}}
        })
    

    def test_can_get_metal_coordinate_bond(self):
        data = self.client.execute("""{metal(id: 1) {
         coordinateBond(id: 1) { id atom { id }}
        }}""")
        self.assertEqual(data, {
         "data": {"metal": {"coordinateBond": {"id": "1", "atom": {"id": "20"}}}}
        })
    

    def test_can_get_metal_coordinate_bonds(self):
        data = self.client.execute("""{metal(id: 1) {
         coordinateBonds { edges { node { id atom { id }}}}
        }}""")
        self.assertEqual(data, {"data": {"metal": {"coordinateBonds": {"edges": [
         {"node": {"id": "1", "atom": {"id": "20"}}},
         {"node": {"id": "2", "atom": {"id": "30"}}},
         {"node": {"id": "3", "atom": {"id": "7"}}}
        ]}}}})
