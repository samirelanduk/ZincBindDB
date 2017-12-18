from time import sleep
from mixer.backend.django import mixer
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from zincbind.models import ZincSite, Pdb
from .base import BrowserTest

class MainSearchTests(BrowserTest):

    def check_term_returns_results(self, term, results):
        self.get("/")
        search = self.browser.find_element_by_id("site-search")

        # The user searches for the term
        term_input = search.find_element_by_tag_name("input")
        term_input.send_keys(term)
        term_input.send_keys(Keys.ENTER)
        sleep(0.4)

        # They are on the search page
        self.check_page("/search?term=" + term.replace(" ", "+"))
        self.check_title("Search Results")
        self.check_h1("Search Results: " + term)

        # There is a result count
        result_count = self.browser.find_element_by_id("result-count")
        self.assertIn("{} result".format(len(results)), result_count.text)
        self.assertIn("Page 1 of 1", result_count.text)

        # There are no pagination links
        self.assertEqual(len(self.browser.find_elements_by_class_name("page-links")), 0)

        # The results are below
        results_table = self.browser.find_element_by_tag_name("table")
        th = results_table.find_element_by_tag_name("tr")
        self.assertEqual(th.find_elements_by_tag_name("th")[0].text, "ZincSite ID")
        self.assertEqual(th.find_elements_by_tag_name("th")[1].text, "PDB")
        self.assertEqual(th.find_elements_by_tag_name("th")[2].text, "Deposited")
        self.assertEqual(th.find_elements_by_tag_name("th")[3].text, "Resolution")
        self.assertEqual(th.find_elements_by_tag_name("th")[4].text, "Organism")
        for row, result in zip(results_table.find_elements_by_tag_name("tr")[1:], results):
            self.assertEqual(row.find_element_by_tag_name("td").text, result)

        # They link to the right page
        link = row.find_elements_by_tag_name("td")[0]
        self.click(link.find_element_by_tag_name("a"))
        self.check_page("/{}/".format(results[-1]))


    def test_needs_term(self):
        self.get("/")
        search = self.browser.find_element_by_id("site-search")

        # The user searches for the term
        term_input = search.find_element_by_tag_name("input")
        term_input.send_keys(Keys.ENTER)
        sleep(0.4)

        # They are still on the home page
        self.check_page("/")

        # There is an error message
        search = self.browser.find_element_by_id("site-search")
        error = search.find_element_by_class_name("error-message")
        self.assertIn("enter a", error.text)


    def test_zero_results(self):
        self.get("/")
        search = self.browser.find_element_by_id("site-search")

        # The user searches for the term
        term_input = search.find_element_by_tag_name("input")
        term_input.send_keys("spiggldywiggle")
        term_input.send_keys(Keys.ENTER)
        sleep(0.4)

        # They are on the search page
        self.check_page("/search?term=spiggldywiggle")
        self.check_title("Search Results")
        self.check_h1("Search Results: spiggldywiggle")

        # There is a result count
        result_count = self.browser.find_element_by_id("result-count")
        self.assertIn("0 results", result_count.text)
        self.assertNotIn("Page", result_count.text)

        # There is no table
        tables = self.browser.find_elements_by_tag_name("table")
        self.assertEqual(len(tables), 0)


    def test_can_search_by_id(self):
        self.check_term_returns_results("1aada200", ["1AADA200"])


    def test_can_search_pdbs(self):
        self.check_term_returns_results("1aad", ["1AADA200", "1AADB200"])


    def test_can_search_titles(self):
        self.check_term_returns_results("PDB 4", ["1AADA200", "1AADB200"])


    def test_can_search_organisms(self):
        self.check_term_returns_results("Mus musculus", ["2AACE500", "1AABA100"])


    def test_can_search_expression(self):
        self.check_term_returns_results(
         "e. coli", ["2AACE500", "1AADA200", "1AADB200", "1AABA100"]
        )


    def test_can_search_technique(self):
        self.check_term_returns_results("NMR", ["2AACE500", "1AADA200", "1AADB200"])


    def test_can_search_classification(self):
        self.check_term_returns_results("immunoglobulin", ["2AACE500"])


    def test_all_results(self):
        self.check_term_returns_results("*", ["2AACE500", "1AADA200", "1AADB200", "1AABA100"])


    def test_paginated_results(self):
        for i in range(110):
            ZincSite.objects.create(
             id="1AAD{}".format(i), x=1.5, y=2.5, z=2.5, pdb=Pdb.objects.get(id="1AAD")
            )
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
        self.assertEqual(len(results.find_elements_by_tag_name("tr")), 27)

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
        self.assertEqual(len(results.find_elements_by_tag_name("tr")), 27)

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



class AdvancedSearchTests(BrowserTest):

    def check_advanced_search(self, dropdown_value, name, term, results):
        # User goes to the search page
        self.get("/")
        nav = self.browser.find_element_by_tag_name("nav")
        self.click(nav.find_elements_by_tag_name("a")[0])
        self.check_page("/search/")
        self.check_title("Advanced Search")
        self.check_h1("Advanced Search")

        # There is a form with a single search row
        form = self.browser.find_element_by_tag_name("form")
        search_rows = form.find_elements_by_class_name("search-row")
        self.assertEqual(len(search_rows), 1)
        row = search_rows[0]

        # They search for sites
        drowndown = row.find_element_by_tag_name("select")
        drowndown = Select(drowndown)
        drowndown.select_by_visible_text(dropdown_value)
        text = row.find_element_by_tag_name("input")
        text.send_keys(term)
        submit = form.find_elements_by_tag_name("input")[-1]
        self.click(submit)

        # They are on the search results page
        self.check_page("/search?{}={}".format(name, term.replace(" ", "+")))
        self.check_title("Search Results")
        self.check_h1("Search Results")

        # There is a result count
        result_count = self.browser.find_element_by_id("result-count")
        self.assertIn(str(len(results)) + " result", result_count.text)
        self.assertIn("Page 1 of 1", result_count.text)

        # There are no pagination links
        self.assertEqual(len(self.browser.find_elements_by_class_name("page-links")), 0)

        # The results are below
        results_table = self.browser.find_element_by_tag_name("table")
        th = results_table.find_element_by_tag_name("tr")
        self.assertEqual(th.find_elements_by_tag_name("th")[0].text, "ZincSite ID")
        self.assertEqual(th.find_elements_by_tag_name("th")[1].text, "PDB")
        self.assertEqual(th.find_elements_by_tag_name("th")[2].text, "Deposited")
        self.assertEqual(th.find_elements_by_tag_name("th")[3].text, "Resolution")
        self.assertEqual(th.find_elements_by_tag_name("th")[4].text, "Organism")
        for row, result in zip(results_table.find_elements_by_tag_name("tr")[1:], results):
            self.assertEqual(row.find_element_by_tag_name("td").text, result)


    def test_can_search_by_title(self):
        self.check_advanced_search("PDB Title", "title", "B 7", ["2AACE500"])


    def test_can_search_by_organism(self):
        self.check_advanced_search("PDB Organism", "organism", "mus m", ["2AACE500", "1AABA100"])


    def test_can_search_by_pdb_code(self):
        self.check_advanced_search("PDB Code", "code", "1aA", ["1AADA200", "1AADB200", "1AABA100"])


    def test_can_search_by_multiple_criteria(self):
        # User goes to the search page
        self.get("/")
        nav = self.browser.find_element_by_tag_name("nav")
        self.click(nav.find_elements_by_tag_name("a")[0])
        self.check_page("/search/")
        self.check_title("Advanced Search")
        self.check_h1("Advanced Search")

        # There is a form with a single search row
        form = self.browser.find_element_by_tag_name("form")
        search_rows = form.find_elements_by_class_name("search-row")
        self.assertEqual(len(search_rows), 1)

        # There is a button for adding more rows
        button = form.find_elements_by_tag_name("button")[-1]
        button.click()
        search_rows = form.find_elements_by_class_name("search-row")
        self.assertEqual(len(search_rows), 2)
        button.click()
        search_rows = form.find_elements_by_class_name("search-row")
        self.assertEqual(len(search_rows), 3)

        # The rows can be removed down to the last
        self.click(search_rows[-1].find_element_by_tag_name("button"))
        search_rows = form.find_elements_by_class_name("search-row")
        self.assertEqual(len(search_rows), 2)
        search_rows[-1].find_element_by_tag_name("button").click()
        search_rows = form.find_elements_by_class_name("search-row")
        self.assertEqual(len(search_rows), 1)
        self.assertFalse(search_rows[-1].find_elements_by_tag_name("button"))
        button.click()
        search_rows = form.find_elements_by_class_name("search-row")
        self.assertEqual(len(search_rows), 2)

        # User searches for sites with organism mus m and code 1aa
        drowndown = search_rows[0].find_element_by_tag_name("select")
        drowndown = Select(drowndown)
        drowndown.select_by_visible_text("PDB Organism")
        text = search_rows[0].find_element_by_tag_name("input")
        text.send_keys("mus m")
        drowndown = search_rows[1].find_element_by_tag_name("select")
        drowndown = Select(drowndown)
        drowndown.select_by_visible_text("PDB Code")
        text = search_rows[1].find_element_by_tag_name("input")
        text.send_keys("1aa")
        submit = form.find_elements_by_tag_name("input")[-1]
        self.click(submit)

        # They are on the search results page
        self.check_page("/search?organism=mus+m&code=1aa")
        self.check_title("Search Results")
        self.check_h1("Search Results")

        # There is a result count
        result_count = self.browser.find_element_by_id("result-count")
        self.assertIn("1 result", result_count.text)
        self.assertIn("Page 1 of 1", result_count.text)

        # There are no pagination links
        self.assertEqual(len(self.browser.find_elements_by_class_name("page-links")), 0)

        # The results are below
        results_table = self.browser.find_element_by_tag_name("table")
        th = results_table.find_element_by_tag_name("tr")
        self.assertEqual(th.find_elements_by_tag_name("th")[0].text, "ZincSite ID")
        self.assertEqual(th.find_elements_by_tag_name("th")[1].text, "PDB")
        self.assertEqual(th.find_elements_by_tag_name("th")[2].text, "Deposited")
        self.assertEqual(th.find_elements_by_tag_name("th")[3].text, "Resolution")
        self.assertEqual(th.find_elements_by_tag_name("th")[4].text, "Organism")
        results = ["1AABA100"]
        for row, result in zip(results_table.find_elements_by_tag_name("tr")[1:], results):
            self.assertEqual(row.find_element_by_tag_name("td").text, result)


    def test_only_entered_text_used(self):
        # User goes to the search page
        self.get("/")
        nav = self.browser.find_element_by_tag_name("nav")
        self.click(nav.find_elements_by_tag_name("a")[0])
        self.check_page("/search/")
        self.check_title("Advanced Search")
        self.check_h1("Advanced Search")

        # There is a form with a single search row
        form = self.browser.find_element_by_tag_name("form")
        search_rows = form.find_elements_by_class_name("search-row")
        self.assertEqual(len(search_rows), 1)

        # There is a button for adding more rows
        button = form.find_elements_by_tag_name("button")[-1]
        button.click()
        search_rows = form.find_elements_by_class_name("search-row")
        self.assertEqual(len(search_rows), 2)
        button.click()
        search_rows = form.find_elements_by_class_name("search-row")
        self.assertEqual(len(search_rows), 3)
        button.click()
        search_rows = form.find_elements_by_class_name("search-row")
        self.assertEqual(len(search_rows), 4)
        button.click()
        search_rows = form.find_elements_by_class_name("search-row")
        self.assertEqual(len(search_rows), 5)

        # The second and fourth inputs are used
        drowndown = search_rows[1].find_element_by_tag_name("select")
        drowndown = Select(drowndown)
        drowndown.select_by_visible_text("PDB Organism")
        text = search_rows[1].find_element_by_tag_name("input")
        text.send_keys("mus m")
        drowndown = search_rows[2].find_element_by_tag_name("select")
        drowndown = Select(drowndown)
        drowndown.select_by_visible_text("PDB Code")
        text = search_rows[2].find_element_by_tag_name("input")
        text.send_keys("1aa")
        submit = form.find_elements_by_tag_name("input")[-1]
        self.click(submit)

        # The correct parameters were sent
        self.check_page("/search?organism=mus+m&code=1aa")


    def test_advanced_search_needs_input(self):
        # User goes to the search page
        self.get("/")
        nav = self.browser.find_element_by_tag_name("nav")
        self.click(nav.find_elements_by_tag_name("a")[0])
        self.check_page("/search/")
        self.check_title("Advanced Search")
        self.check_h1("Advanced Search")

        # There is a form with a single search row
        form = self.browser.find_element_by_tag_name("form")
        search_rows = form.find_elements_by_class_name("search-row")
        self.assertEqual(len(search_rows), 1)

        # They submit without sending anything
        submit = form.find_elements_by_tag_name("input")[-1]
        self.click(submit)

        # They are still on the search page
        self.check_page("/search/")

        # There is an error message
        form = self.browser.find_element_by_tag_name("form")
        error = form.find_element_by_class_name("error-message")
        self.assertIn("enter", error.text)

