from mixer.backend.django import mixer
from .base import FunctionalTest
from zinc.models import *
from datetime import date, timedelta

class SearchTest(FunctionalTest):

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
        info = self.browser.find_element_by_class_name("box")
        if not pdbs:
            self.assertIn("no results", info.text)
            self.assertIn("PDB codes", info.text)
            self.assertIn("PDB descriptions", info.text)
        else:
            self.assertIn("{} result".format(len(pdbs)), info.text)
        results = self.browser.find_elements_by_class_name("pdb-result")
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
        with self.assertRaises(self.NoElement):
            self.browser.find_element_by_id("search-nav")


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
        self.check_basic_search("bacillus", ["1B21", "1A6F"])
        self.check_basic_search("HEME", ["6H8P"])


    def test_can_paginate_search_results(self):
        self.populate_filler()

        # User searches for the fillers
        self.get("/")
        self.quick_search("filler")

        # They are on the search page
        self.check_page("/search?q=filler")
        self.check_title("Search Results: filler")

        # The search information is there.
        self.check_search_page_correct(105, (1, 5), 25, "PDB: A104", "PDB: A80")

        # There is a link to the next page
        search_nav = self.browser.find_element_by_id("search-nav")
        next_ = search_nav.find_element_by_class_name("next-page")
        with self.assertRaises(self.NoElement):
            search_nav.find_element_by_class_name("previous-page")
        self.click(next_)
        self.check_page("/search?q=filler&page=2")

        # The second page is correct
        self.check_search_page_correct(105, (2, 5), 25, "PDB: A79", "PDB: A55")

        # They keep going to the end
        for page in (2, 3, 4):
            self.check_page(f"/search?q=filler&page={page}")
            self.check_search_page_correct(105, (page, 5), 25)
            search_nav = self.browser.find_element_by_id("search-nav")
            next_ = search_nav.find_element_by_class_name("next-page")
            self.click(next_)

        # The last page is correct
        self.check_page("/search?q=filler&page=5")
        self.check_search_page_correct(105, (5, 5), 5, "PDB: A4", "PDB: A0")
        search_nav = self.browser.find_element_by_id("search-nav")
        previous = search_nav.find_element_by_class_name("previous-page")
        with self.assertRaises(self.NoElement):
            search_nav.find_element_by_class_name("next-page")

        # They can go back
        for page in (5, 4, 3, 2):
            self.check_page(f"/search?q=filler&page={page}")
            info = self.browser.find_element_by_class_name("box")
            self.assertIn(f"Page {page} of 5", info.text)
            search_nav = self.browser.find_element_by_id("search-nav")
            previous_ = search_nav.find_element_by_class_name("previous-page")
            self.click(previous_)
        self.check_page("/search?q=filler&page=1")
        self.check_search_page_correct(105, (1, 5), 25, "PDB: A104", "PDB: A80")

        # They can go to last and first pages
        search_nav = self.browser.find_element_by_id("search-nav")
        last = search_nav.find_element_by_class_name("last-page")
        self.click(last)
        self.check_page("/search?q=filler&page=5")
        search_nav = self.browser.find_element_by_id("search-nav")
        first = search_nav.find_element_by_class_name("first-page")
        self.click(first)
        self.check_page("/search?q=filler&page=1")


    def test_can_handle_malformed_search_urls(self):
        self.populate_filler()
        self.get("/search?q=filler&page=100")
        self.check_title("Page Not Found")
        self.get("/search?q=filler&page=ABC")
        self.check_title("Page Not Found")
