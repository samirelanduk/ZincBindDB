from .base import FunctionalTest
from zinc.models import *
import requests

class APISearchingTests(FunctionalTest):

    def check_basic_search(self, term, pdbs):
        r = requests.get(self.live_server_url + "/api/search?q=" + term)
        json = r.json()
        self.assertEqual(json["count"], len(pdbs))
        for pdb, result in zip(pdbs, json["results"]):
            pdb = Pdb.objects.get(id=pdb)
            self.assertEqual(pdb.id, result["id"])
            self.assertEqual(pdb.title, result["title"])
            self.assertEqual(pdb.zincsite_set.count(), len(result["zincsites"]))


    def check_advanced_search(self, terms, pdbs):
        r = requests.get(self.live_server_url + "/api/search?" + "&".join(["{}={}".format(key, value) for key, value in terms.items()]))
        json = r.json()
        self.assertEqual(json["count"], len(pdbs))


    def test_basic_search_no_results(self):
        self.check_basic_search("xaphania", [])


    def test_api_quick_search(self):
        self.check_basic_search("1zEh", ["1ZEH"])
        self.check_basic_search("Structure+of", ["6EQU", "1BYF", "1ZEH"])
        self.check_basic_search("electron+microscopy", ["4UXY"])
        self.check_basic_search("antibody", ["1A0Q"])
        self.check_basic_search("bacillus", ["1B21", "1A6F"])
        self.check_basic_search("HEME", ["6H8P"])


    def test_api_advanced_search(self):
        self.check_advanced_search({"title": "Structure of"}, ["6EQU", "1BYF", "1ZEH"])
        self.check_advanced_search({"classification": "Antibody"}, ["1A0Q"])
        self.check_advanced_search({"keywords": "HEME"}, ["6H8P"])
        self.check_advanced_search({"organism": "bacillus"}, ["1B21", "1A6F"])
        self.check_advanced_search({"expression": "BL21"}, ["6H8P", "6EQU"])
        self.check_advanced_search({"technique": "electron microscopy"}, ["4UXY"])
        self.check_advanced_search({"resolution_lt": "1.7"}, ["6EQU", "1ZEH"])
        self.check_advanced_search({"resolution_gt": "6"}, ["4UXY"])
        self.check_advanced_search({"rfactor_lt": "0.18"}, ["6EQU", "1ZEH"])
        self.check_advanced_search({"rfactor_gt": "0.2"}, ["1BYF", "1A6F", "1A0Q"])
        self.check_advanced_search({"deposited_gt": "2017-01-01"}, ["6H8P", "6EQU"])
        self.check_advanced_search({"deposited_lt": "2000-01-01"}, ["1B21", "1BYF", "1ZEH", "1A6F", "1A0Q"])
        self.check_advanced_search({
         "rfactor_lt": "0.18", "deposited_lt": "2000-01-01"
        }, ["1ZEH"])
