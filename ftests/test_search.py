from time import sleep
from mixer.backend.django import mixer
from selenium.webdriver.common.keys import Keys
from zincbind.models import ZincSite
from .base import BrowserTest

class MainSearchTests(BrowserTest):

    def test_can_search_by_id(self):
        self.get("/")
        search = self.browser.find_element_by_id("site-search")

        # The user searches for '1AADA200'
        term = search.find_element_by_tag_name("input")
        term.send_keys("1aada200")
        term.send_keys(Keys.ENTER)
        sleep(0.4)

        # They are on the search page
        self.check_page("/search?term=1aada200")
        self.check_title("Search Results")
        self.check_h1("Search Results: 1aada200")

        # There is a result count
        result_count = self.browser.find_element_by_id("result-count")
        self.assertIn("1 result", result_count.text)
        self.assertIn("Page 1 of 1", result_count.text)

        # There are no pagination links
        self.assertEqual(len(self.browser.find_elements_by_class_name("page-links")), 0)

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
        self.click(link.find_element_by_tag_name("a"))
        self.check_page("/1AADA200/")


    def test_can_search_pdbs(self):
        self.get("/")
        search = self.browser.find_element_by_id("site-search")

        # The user searches for '1AAD'
        term = search.find_element_by_tag_name("input")
        term.send_keys("1aad")
        term.send_keys(Keys.ENTER)
        sleep(0.4)

        # They are on the search page
        self.check_page("/search?term=1aad")
        self.check_title("Search Results")
        self.check_h1("Search Results: 1aad")

        # There is a result count
        result_count = self.browser.find_element_by_id("result-count")
        self.assertIn("2 results", result_count.text)
        self.assertIn("Page 1 of 1", result_count.text)

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

        # There are no pagination links
        self.assertEqual(len(self.browser.find_elements_by_class_name("page-links")), 0)


    def test_paginated_results(self):
        for i in range(110):
            ZincSite.objects.create(id="1AAD{}".format(i), x=1.5, y=2.5, z=2.5)
        self.get("/")
        search = self.browser.find_element_by_id("site-search")

        # The user searches for '1AAD'
        term = search.find_element_by_tag_name("input")
        term.send_keys("1aad")
        term.send_keys(Keys.ENTER)
        sleep(0.4)

        # They are on the search page
        self.check_page("/search?term=1aad")
        self.check_title("Search Results")
        self.check_h1("Search Results: 1aad")

        # There are 25 results
        result_count = self.browser.find_element_by_id("result-count")
        self.assertIn("112 results", result_count.text)
        self.assertIn("Page 1 of 5", result_count.text)
        results = self.browser.find_element_by_tag_name("table")
        self.assertEqual(len(results.find_elements_by_tag_name("tr")), 26)

        # There is a page link to the next page
        links = self.browser.find_element_by_class_name("page-links")
        self.assertEqual(len(links.find_elements_by_tag_name("a")), 1)
        link = links.find_element_by_tag_name("a")
        self.click(link)
        self.check_page("/search?term=1aad&page=2")
        self.check_title("Search Results")
        self.check_h1("Search Results: 1aad")

        # There are still 25 results
        result_count = self.browser.find_element_by_id("result-count")
        self.assertIn("112 results", result_count.text)
        self.assertIn("Page 2 of 5", result_count.text)
        results = self.browser.find_element_by_tag_name("table")
        self.assertEqual(len(results.find_elements_by_tag_name("tr")), 26)

        # There are page links
        links = self.browser.find_element_by_class_name("page-links")
        self.assertEqual(len(links.find_elements_by_tag_name("a")), 2)
        link = links.find_element_by_tag_name("a")
        self.click(link)
        self.check_page("/search?term=1aad&page=1")
        self.check_title("Search Results")
        self.check_h1("Search Results: 1aad")

        # They go to the last page
        for index in range(2, 6):
            links = self.browser.find_element_by_class_name("page-links")
            link = links.find_elements_by_tag_name("a")[-1]
            self.click(link)
            result_count = self.browser.find_element_by_id("result-count")
            self.assertIn("112 results", result_count.text)
            self.assertIn("Page {} of 5".format(index), result_count.text)

