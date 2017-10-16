from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from zincsites.models import Pdb, Residue, ZincSite

class FunctionalTest(StaticLiveServerTestCase):

    def setUp(self):
        self.user = User.objects.create_user(
         username="testuser",
         password="testpassword"
        )
        pdb = Pdb.objects.create(
         id="5O8H", deposition_date="2017-10-11",
         title="CRYSTAL STRUCTURE OF R. RUBER ADH-A, MUTANT Y294F, W295A, F43H, H39Y"
        )
        r1 = Residue.objects.create(id="A92", number=92, name="CYS", chain="A", pdb=pdb)
        r2 = Residue.objects.create(id="A95", number=95, name="CYS", chain="A", pdb=pdb)
        r3 = Residue.objects.create(id="A98", number=98, name="CYS", chain="A", pdb=pdb)
        r4 = Residue.objects.create(id="A106", number=106, name="CYS", chain="A", pdb=pdb)
        site = ZincSite.objects.create(id="508HA501")
        site.residues.add(r1)
        site.residues.add(r2)
        site.residues.add(r3)
        site.residues.add(r4)

        self.browser = webdriver.Chrome()
        self.browser.set_window_size(800, 700)


    def tearDown(self):
        self.browser.quit()


    def login(self):
        self.client.login(username="testuser", password="testpassword")
        cookie = self.client.cookies["sessionid"].value
        self.browser.get(self.live_server_url + "/")
        self.browser.add_cookie({
         "name": "sessionid", "value": cookie, "secure": False, "path": "/"
        })
        self.browser.refresh()


    def get(self, url):
        self.browser.get(self.live_server_url + url)


    def check_page(self, url):
        self.assertEqual(self.browser.current_url, self.live_server_url + url)


    def check_title(self, text):
        self.assertIn(text, self.browser.title)


    def check_h1(self, text):
        self.assertIn(text, self.browser.find_element_by_tag_name("h1").text)


    def input_site(self, pdb, zincid, res1, res2, res3):
        # There is a form
        site_form = self.browser.find_element_by_tag_name("form")

        # They enter the PDB code
        pdb_input = site_form.find_elements_by_tag_name("input")[0]
        pdb_input.send_keys(pdb)

        # They enter the zinc ID
        zinc_input = site_form.find_elements_by_tag_name("input")[1]
        zinc_input.send_keys(zincid)

        # They enter the residues
        residue_input_div = site_form.find_element_by_id("residue-inputs")
        inputs = residue_input_div.find_elements_by_tag_name("input")
        self.assertEqual(len(inputs), 1)
        inputs[0].send_keys(res1)
        buttons = residue_input_div.find_elements_by_tag_name("button")
        self.assertEqual(len(buttons), 2)
        buttons[-1].click()
        inputs = residue_input_div.find_elements_by_tag_name("input")
        self.assertEqual(len(inputs), 2)
        inputs[1].send_keys(res2)
        buttons = residue_input_div.find_elements_by_tag_name("button")
        self.assertEqual(len(buttons), 3)
        self.browser.execute_script(
         "window.scrollTo(0, document.body.scrollHeight);"
        )
        buttons[-1].click()
        inputs = residue_input_div.find_elements_by_tag_name("input")
        self.assertEqual(len(inputs), 3)
        inputs[2].send_keys("WRONG")
        buttons = residue_input_div.find_elements_by_tag_name("button")
        self.assertEqual(len(buttons), 4)
        buttons[-1].click()
        inputs = residue_input_div.find_elements_by_tag_name("input")
        self.assertEqual(len(inputs), 4)
        inputs[3].send_keys(res3)
        buttons = residue_input_div.find_elements_by_tag_name("button")
        self.assertEqual(len(buttons), 5)
        buttons[-3].click()
        inputs = residue_input_div.find_elements_by_tag_name("input")
        self.assertEqual(len(inputs), 3)
        buttons = residue_input_div.find_elements_by_tag_name("button")
        self.assertEqual(len(buttons), 4)

        # They submit the site
        submit_button = zinc_input = site_form.find_elements_by_tag_name("input")[-1]
        submit_button.click()


    def check_site_page(self, pdb, date, title, residue_ids, residue_names):
        # There is a PDB section
        pdb_section = self.browser.find_element_by_id("site-pdb")
        pdb_title = pdb_section.find_element_by_tag_name("h2")
        self.assertIn("PDB", pdb_title.text)
        table = pdb_section.find_element_by_tag_name("table")
        rows = table.find_elements_by_tag_name("tr")
        self.assertEqual(
         rows[0].find_elements_by_tag_name("td")[0].text, "PDB Code"
        )
        self.assertEqual(
         rows[1].find_elements_by_tag_name("td")[0].text, "Deposition Date"
        )
        self.assertEqual(
         rows[2].find_elements_by_tag_name("td")[0].text, "Title"
        )
        self.assertEqual(
         rows[0].find_elements_by_tag_name("td")[1].text, pdb
        )
        self.assertEqual(
         rows[1].find_elements_by_tag_name("td")[1].text, date
        )
        self.assertIn(
         title, rows[2].find_elements_by_tag_name("td")[1].text,
        )

        # There is a residues section
        residues_section = self.browser.find_element_by_id("site-residues")
        residues_title = residues_section.find_element_by_tag_name("h2")
        self.assertIn("Residues", residues_section.text)

        # There are residue divs
        residue_divs = self.browser.find_elements_by_class_name("residue")
        self.assertEqual(len(residue_divs), len(residue_ids))

        # The residue divs are correct
        for index, residue_div in enumerate(residue_divs):
            table = residue_div.find_element_by_tag_name("table")
            rows = table.find_elements_by_tag_name("tr")
            self.assertEqual(
             rows[0].find_elements_by_tag_name("td")[0].text, "Chain"
            )
            self.assertEqual(
             rows[1].find_elements_by_tag_name("td")[0].text, "ID"
            )
            self.assertEqual(
             rows[2].find_elements_by_tag_name("td")[0].text, "Name"
            )
            self.assertEqual(
             rows[0].find_elements_by_tag_name("td")[1].text, residue_ids[index][0]
            )
            self.assertEqual(
             rows[1].find_elements_by_tag_name("td")[1].text, residue_ids[index]
            )
            self.assertEqual(
             rows[2].find_elements_by_tag_name("td")[1].text, residue_names[index]
            )
