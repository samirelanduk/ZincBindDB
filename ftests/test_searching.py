from .base import FunctionalTest

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
        self.assertIn("SUPERB PDB", results[0].text)
        self.assertIn("2.1 Å", results[0].text)
        self.assertIn("X-RAY", results[0].text)
        self.assertIn("REDUCTASE", results[0].text)
