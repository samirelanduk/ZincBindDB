from .base import FunctionalTest
from zinc.models import *
from datetime import date, timedelta

class QuickSearchTests(FunctionalTest):

    def quick_search(self, term):
        search = self.browser.find_element_by_id("site-search")
        search_form = search.find_element_by_tag_name("form")
        inputs = search_form.find_elements_by_tag_name("input")
        inputs[0].send_keys(term)
        self.click(inputs[1])


    def test_basic_search_no_results(self):
        # User searches for something that has no results
        self.get("/")
        self.quick_search("PlibblePlebblePlunk")

        # They are on the search page
        self.check_page("/search?q=PlibblePlebblePlunk")
        self.check_title("Search Results: PlibblePlebblePlunk")

        # The search information is there
        info = self.browser.find_element_by_class_name("search-info")
        self.assertIn("no results", info.text)
        self.assertIn("PDB codes", info.text)
        self.assertIn("PDB descriptions", info.text)

        # There are no results
        results = self.browser.find_elements_by_class_name("pdb-result")
        self.assertEqual(len(results), 0)


    def test_can_search_pdb_codes(self):
        # User searches for PDB code
        self.get("/")
        self.quick_search("a001")

        # They are on the search page
        self.check_page("/search?q=a001")
        self.check_title("Search Results: a001")

        # The search information is there.
        info = self.browser.find_element_by_class_name("search-info")
        self.assertIn("1 result", info.text)

        # There is one result
        results = self.browser.find_elements_by_class_name("pdb-result")
        self.assertEqual(len(results), 1)

        # The result contains the correct information
        self.assertIn("PDB: A001", results[0].text)
        self.assertIn("28 September, 1990", results[0].text)
        self.assertIn("Felis catus", results[0].text)
        self.assertIn("SUPERB PDB FILE", results[0].text)
        self.assertIn("2.1 Å", results[0].text)
        self.assertIn("X-RAY (2.1 Å)", results[0].text)
        self.assertIn("REDUCTASE", results[0].text)
        self.assertIn("2 zinc-bearing chains", results[0].text)

        # There is no search nav
        with self.assertRaises(self.NoElement):
            self.browser.find_element_by_id("search-nav")



    def test_can_search_pdb_titles(self):
        # User searches for PDB code
        self.get("/")
        self.quick_search("PDB file")

        # They are on the search page
        self.check_page("/search?q=PDB+file")
        self.check_title("Search Results: PDB file")

        # The search information is there.
        info = self.browser.find_element_by_class_name("search-info")
        self.assertIn("2 results", info.text)

        # There are two results
        results = self.browser.find_elements_by_class_name("pdb-result")
        self.assertEqual(len(results), 2)
        self.assertIn("PDB: A002", results[0].text)
        self.assertIn("28 September, 1992", results[0].text)
        self.assertIn("X-RAY", results[1].text)
        self.assertIn("PDB: A001", results[1].text)
        self.assertIn("28 September, 1990", results[1].text)
        self.assertIn("X-RAY (2.1 Å)", results[1].text)


    def test_can_paginate_search_results(self):
        for n in range(105):
            Pdb.objects.create(
             id=f"A{n}", title="FILLER", skeleton=False,
             deposited=date(1990, 9, 28) + timedelta(days=n)
            )

        # User searches for the fillers
        self.get("/")
        self.quick_search("filler")

        # They are on the search page
        self.check_page("/search?q=filler")
        self.check_title("Search Results: filler")

        # The search information is there.
        info = self.browser.find_element_by_class_name("search-info")
        self.assertIn("105 results", info.text)
        self.assertIn("Page 1 of 5", info.text)

        # The first 25 results are on the page
        results = self.browser.find_elements_by_class_name("pdb-result")
        self.assertEqual(len(results), 25)
        self.assertIn("PDB: A104", results[0].text)
        self.assertIn("PDB: A80", results[24].text)

        # There is a link to the next page
        search_nav = self.browser.find_element_by_id("search-nav")
        next_ = search_nav.find_element_by_class_name("next-page")
        with self.assertRaises(self.NoElement):
            search_nav.find_element_by_class_name("previous-page")
        self.click(next_)
        self.check_page("/search?q=filler&page=2")

        # The second page is correct
        info = self.browser.find_element_by_class_name("search-info")
        self.assertIn("105 results", info.text)
        self.assertIn("Page 2 of 5", info.text)
        results = self.browser.find_elements_by_class_name("pdb-result")
        self.assertEqual(len(results), 25)
        self.assertIn("PDB: A79", results[0].text)
        self.assertIn("PDB: A55", results[24].text)

        # They keep going to the end
        for page in (2, 3, 4):
            self.check_page(f"/search?q=filler&page={page}")
            info = self.browser.find_element_by_class_name("search-info")
            self.assertIn(f"Page {page} of 5", info.text)
            results = self.browser.find_elements_by_class_name("pdb-result")
            self.assertEqual(len(results), 25)
            search_nav = self.browser.find_element_by_id("search-nav")
            next_ = search_nav.find_element_by_class_name("next-page")
            self.click(next_)

        # The last page is correct
        self.check_page("/search?q=filler&page=5")
        info = self.browser.find_element_by_class_name("search-info")
        self.assertIn("105 results", info.text)
        self.assertIn("Page 5 of 5", info.text)
        results = self.browser.find_elements_by_class_name("pdb-result")
        self.assertEqual(len(results), 5)
        self.assertIn("PDB: A4", results[0].text)
        self.assertIn("PDB: A0", results[4].text)
        search_nav = self.browser.find_element_by_id("search-nav")
        previous = search_nav.find_element_by_class_name("previous-page")
        with self.assertRaises(self.NoElement):
            search_nav.find_element_by_class_name("next-page")

        # They can go back
        for page in (5, 4, 3, 2):
            self.check_page(f"/search?q=filler&page={page}")
            info = self.browser.find_element_by_class_name("search-info")
            self.assertIn(f"Page {page} of 5", info.text)
            search_nav = self.browser.find_element_by_id("search-nav")
            previous_ = search_nav.find_element_by_class_name("previous-page")
            self.click(previous_)
        self.check_page("/search?q=filler&page=1")
        info = self.browser.find_element_by_class_name("search-info")
        self.assertIn("105 results", info.text)
        self.assertIn("Page 1 of 5", info.text)
        results = self.browser.find_elements_by_class_name("pdb-result")
        self.assertEqual(len(results), 25)


    def test_can_handle_malformed_search_urls(self):
        for n in range(105):
            Pdb.objects.create(
             id=f"A{n}", title="FILLER", skeleton=False,
             deposited=date(1990, 9, 28) + timedelta(days=n)
            )
        self.get("/search?q=filler&page=100")
        self.check_title("Page Not Found")
        self.get("/search?q=filler&page=ABC")
        self.check_title("Page Not Found")
