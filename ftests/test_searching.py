from .base import FunctionalTest

class QuickSearchTests(FunctionalTest):

    def test_can_search_pdb_codes(self):
        # User searches for PDB code
        self.get("/")
        search = self.browser.find_element_by_id("site-search")
        search_form = search.find_element_by_tag_name("form")
        inputs = search_form.find_elements_by_tag_name("input")
        inputs[0].send_keys("A00")
        self.click(inputs[1])

        # They are on the search page
        self.check_page("/search?q=A00")
        self.check_title("Search Results: A00")
