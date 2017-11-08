from time import sleep
from .base import BrowserTest

class MainSearchTests(BrowserTest):

    def test_can_search_by_id(self):
        self.get("/")
        search = self.browser.find_element_by_id("site-search")

        # The user searches for '1AADA200'
        term = search.find_element_by_tag_name("input")
        term.send_keys("1aada200")
        submit = search.find_elements_by_tag_name("input")[-1]
        submit.click()

        # They are on the search page
        self.check_page("/search/")
        self.check_title("Search Results")
        self.check_h1("Search Results: 1aada200")

        # There is a result count
        result_count = self.browser.find_element_by_id("result-count")
        self.assertIn("1 result", result_count.text)
