from mixer.backend.django import mixer
from .base import FunctionalTest
from core.models import *
from datetime import date, timedelta

class SearchTest(FunctionalTest):

    def check_results(self, pdbs):
        info = self.browser.find_element_by_class_name("box")
        if not pdbs:
            self.assertIn("no results", info.text)
            self.assertIn("PDB codes", info.text)
            self.assertIn("PDB descriptions", info.text)
        else:
            self.assertIn("{} result".format(len(pdbs)), info.text)
        results = self.browser.find_elements_by_class_name("search-result")
        self.assertEqual(len(results), len(pdbs))
        for pdb, result in zip(pdbs, results):
            pdb = Pdb.objects.get(id=pdb)
            self.assertIn("PDB: " + pdb.id, result.text)
            self.assertIn(str(pdb.deposited.year), result.text)
            self.assertIn(pdb.organism.lower(), result.text.lower())
            self.assertIn(pdb.title, result.text)
            self.assertIn(str(pdb.resolution), result.text)
            self.assertIn(pdb.technique, result.text)
            self.assertIn(pdb.classification.replace("  ", " "), result.text)
            self.assertIn("{} zinc-bearing chain".format(pdb.chain_set.count()), result.text)
            sites = result.find_elements_by_class_name("pdb-site")
            self.assertEqual(len(sites), pdb.zincsite_set.count())
            for site, site_div in zip(pdb.zincsite_set.all(), sites):
                self.assertIn(site.id, site_div.text)
                self.assertIn("{} residue".format(site.residue_set.count()), site_div.text)
                for res in site.residue_set.all():
                    self.assertIn(res.atomium_id, site_div.text)
        with self.assertRaises(self.NoElement):
            self.browser.find_element_by_id("search-nav")


    def quick_search(self, term):
        self.get("/")
        search = self.browser.find_element_by_id("site-search")
        search_form = search.find_element_by_tag_name("form")
        inputs = search_form.find_elements_by_tag_name("input")
        inputs[0].send_keys(term)
        self.click(inputs[1])


    def check_basic_search(self, term, pdbs):
        # Search
        self.quick_search(term)

        # Results
        self.check_page("/search?q=" + term.replace(" ", "+"))
        self.check_title("Search Results: " + term)
        self.check_results(pdbs)


    def check_advanced_search(self, terms, pdbs):
        # Search
        self.get("/search/")
        search = self.browser.find_element_by_tag_name("form")
        filled_in = False
        for key, value in terms.items():
            if filled_in:
                self.click(search.find_element_by_tag_name("button"))
            select = search.find_elements_by_tag_name("select")[-1]
            input = search.find_elements_by_tag_name("input")[-2]
            self.select_dropdown(select, key)
            input.send_keys(value)
            filled_in = True
        self.click(search.find_elements_by_tag_name("input")[-1])

        # Results
        self.check_results(pdbs)


    def populate_filler(self):
        for n in range(105):
            mixer.blend(
             Pdb, id=f"A{n}", title="FILLER",
             deposited=date(1990, 9, 28) + timedelta(days=n)
            )


    def check_search_page_correct(self, result_count, page, page_count, first=None, last=None):
        info = self.browser.find_element_by_class_name("box")
        self.assertIn("{} results".format(result_count), info.text)
        self.assertIn("Page {} of {}".format(*page), info.text)
        results = self.browser.find_elements_by_class_name("pdb-result")
        self.assertEqual(len(results), page_count)
        if first: self.assertIn(first, results[0].text)
        if last: self.assertIn(last, results[-1].text)



class QuickSearchTests(SearchTest):

    def test_basic_search_no_results(self):
        self.check_basic_search("xaphania", [])


    def test_can_search_pdb_fields(self):
        self.check_basic_search("1zEh", ["1ZEH"])
        self.check_basic_search("Structure of", ["6EQU", "1BYF", "1ZEH"])
        self.check_basic_search("electron microscopy", ["4UXY"])
        self.check_basic_search("antibody", ["1A0Q"])
        self.check_basic_search("bacillus", ["1B21", "1A6F"])
        self.check_basic_search("HEME", ["6H8P"])


    def test_can_handle_malformed_search_urls(self):
        self.populate_filler()
        self.get("/search?q=filler&page=100")
        self.check_title("Page Not Found")
        self.get("/search?q=filler&page=ABC")
        self.check_title("Page Not Found")



class AdvancedSearchTests(SearchTest):

    def test_can_search_individual_fields(self):
        self.check_advanced_search({"Title contains": "Structure of"}, ["6EQU", "1BYF", "1ZEH"])
        self.check_advanced_search({"Classification contains": "Antibody"}, ["1A0Q"])
        self.check_advanced_search({"Keywords contain": "HEME"}, ["6H8P"])
        self.check_advanced_search({"Organism contains": "bacillus"}, ["1B21", "1A6F"])
        self.check_advanced_search({"Expression System contains": "BL21"}, ["6H8P", "6EQU"])
        self.check_advanced_search({"Technique contains": "electron microscopy"}, ["4UXY"])
        self.check_advanced_search({"Resolution better than": "1.7"}, ["6EQU", "1ZEH"])
        self.check_advanced_search({"Resolution worse than": "6"}, ["4UXY"])
        self.check_advanced_search({"Rfactor better than": "0.18"}, ["6EQU", "1ZEH"])
        self.check_advanced_search({"Rfactor worse than": "0.2"}, ["1BYF", "1A6F", "1A0Q"])
        self.check_advanced_search({"Deposited since": "01012017"}, ["6H8P", "6EQU"])
        self.check_advanced_search({"Deposited before": "01012000"}, ["1B21", "1BYF", "1ZEH", "1A6F", "1A0Q"])


    def test_can_search_multiple_fields(self):
        self.check_advanced_search({
         "Rfactor better than": "0.18", "Deposited before": "01012000"
        }, ["1ZEH"])
