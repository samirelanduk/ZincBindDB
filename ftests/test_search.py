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

        # The results are below
        results = self.browser.find_element_by_tag_name("table")
        th = results.find_element_by_tag_name("tr")
        self.assertEqual(th.find_elements_by_tag_name("th")[0].text, "ZincSite ID")
        self.assertEqual(th.find_elements_by_tag_name("th")[1].text, "PDB")
        self.assertEqual(th.find_elements_by_tag_name("th")[2].text, "Deposited")
        self.assertEqual(th.find_elements_by_tag_name("th")[3].text, "Residues")
        row = results.find_elements_by_tag_name("tr")[1]
        self.assertEqual(row.find_elements_by_tag_name("td")[0].text, "1AADA200")
        self.assertEqual(row.find_elements_by_tag_name("td")[1].text, "1AAD")
        self.assertEqual(row.find_elements_by_tag_name("td")[2].text, "4 January, 2012")
        self.assertEqual(row.find_elements_by_tag_name("td")[3].text, "3")

        # They link to the right page
        link = row.find_elements_by_tag_name("td")[0]
        link.find_element_by_tag_name("a").click()
        self.check_page("/1AADA200/")


    def test_can_search_pdbs(self):
        self.get("/")
        search = self.browser.find_element_by_id("site-search")

        # The user searches for '1AAD'
        term = search.find_element_by_tag_name("input")
        term.send_keys("1aad")
        submit = search.find_elements_by_tag_name("input")[-1]
        submit.click()

        # They are on the search page
        self.check_page("/search/")
        self.check_title("Search Results")
        self.check_h1("Search Results: 1aad")

        # There is a result count
        result_count = self.browser.find_element_by_id("result-count")
        self.assertIn("2 results", result_count.text)

        # The results are below
        results = self.browser.find_element_by_tag_name("table")
        row1 = results.find_elements_by_tag_name("tr")[1]
        self.assertEqual(row1.find_elements_by_tag_name("td")[0].text, "1AADA200")
        self.assertEqual(row1.find_elements_by_tag_name("td")[1].text, "1AAD")
        self.assertEqual(row1.find_elements_by_tag_name("td")[2].text, "4 January, 2012")
        self.assertEqual(row1.find_elements_by_tag_name("td")[3].text, "3")
        row2 = results.find_elements_by_tag_name("tr")[2]
        self.assertEqual(row2.find_elements_by_tag_name("td")[0].text, "1AADB200")
        self.assertEqual(row2.find_elements_by_tag_name("td")[1].text, "1AAD")
        self.assertEqual(row2.find_elements_by_tag_name("td")[2].text, "4 January, 2012")
        self.assertEqual(row2.find_elements_by_tag_name("td")[3].text, "3")
