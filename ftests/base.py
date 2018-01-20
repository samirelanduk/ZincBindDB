import os
import sys
from time import sleep
from datetime import datetime, timedelta
from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from zincbind.models import Pdb, Residue, ZincSite, Atom

class FunctionalTest(StaticLiveServerTestCase):

    def setUp(self):
        # Create 80 empty Pdbs - A001 to A80
        for index in range(1, 81):
            Pdb.objects.create(
             pk="A" + str(index).zfill(3), checked=datetime.now()
            )
        # Create 20 filled in Pdbs - A081 to A100
        for index in range(81, 101):
            day = datetime(2012, 1, 1) + timedelta(days=index - 1)
            Pdb.objects.create(
             id="A" + str(index).zfill(3), checked=datetime.now(),
             title="PDB {}".format(index), deposited=day,
             resolution=5-(index / 10), rfactor=10-(index / 5),
             technique="X RAY" if index % 2 else "NMR",
             organism=None if index % 10 == 0 else "MUS MUSCULUS",
             expression="E. COLI" if index % 3 == 0 else "SYNTH ORG",
             classification="IMMUNOGLOBULIN" if index % 5 == 0 else "LYASE"
            )

        # Create 24 ZincSites - every fifth PDB has two
        for index, pdb in enumerate(Pdb.objects.exclude(deposited=None)):
            site = ZincSite.objects.create(
             id=pdb.id + "A" + str(index * 100), x=1.5, y=2.5, z=2.5,
             pdb=pdb
            )
            for r in range(11, 14):
                residue = Residue.objects.create(
                 id=site.id + "A" + str(r), residue_id="A" + str(r),
                 name="VAL" if r % 2 else "CYS", number=r, chain="A", site=site
                )
                for a in range(1, 5):
                    Atom.objects.create(
                     id=residue.id + str(a + r * 10), x=a, y=a, z=a, charge=0, bfactor=1.5,
                     name=str(a), element="C", atom_id=a + r * 10, residue=residue,
                     alpha=(a == 1), beta=(a == 2), liganding=(a > 2)
                    )
            if index % 5 == 0:
                site = ZincSite.objects.create(
                 id=pdb.id + "B" + str(index * 100), x=1.5, y=2.5, z=2.5,
                 pdb=pdb
                )
                for r in range(11, 14):
                    residue = Residue.objects.create(
                     id=site.id + "B" + str(r), residue_id="B" + str(r),
                     name="VAL" if r % 2 else "CYS", number=r, chain="B", site=site
                    )
                    for a in range(1, 5):
                        Atom.objects.create(
                         id=residue.id + str(a + r * 10), x=a, y=a, z=a, charge=0, bfactor=1.5,
                         name=str(a), element="C", atom_id=a + r * 10, residue=residue,
                         alpha=(a == 1), beta=(a == 2), liganding=(a > 2)
                        )



class BrowserTest(FunctionalTest):

    def setUp(self):
        FunctionalTest.setUp(self)
        self.headless = os.environ.get("djangovar") == "headless"
        if self.headless:
            self.browser = webdriver.PhantomJS()
        else:
            try:
                self.browser = webdriver.Chrome()
            except:
                self.browser = webdriver.Firefox()
        #self.browser.set_window_size(800, 700)


    def tearDown(self):
        self.browser.quit()
        try:
            os.remove("ghostdriver.log")
        except IOError: pass
        try:
            os.remove("geckodriver.log")
        except IOError: pass


    def get(self, url):
        self.browser.get(self.live_server_url + url)


    def check_page(self, url):
        self.assertEqual(self.browser.current_url, self.live_server_url + url)


    def check_title(self, text):
        self.assertIn(text, self.browser.title)


    def check_h1(self, text):
        self.assertIn(text, self.browser.find_element_by_tag_name("h1").text)


    def scroll_to(self, element):
        self.browser.execute_script("arguments[0].scrollIntoView();", element)


    def click(self, element):
        self.scroll_to(element)
        element.click()
        sleep(0.5)


    def check_table_values(self, table, row_values):
        rows = table.find_elements_by_tag_name("tr")
        self.assertEqual(len(rows), len(row_values))
        for table_row, value_row in zip(rows, row_values):
            cells = table_row.find_elements_by_tag_name("td")
            self.assertEqual(len(cells), len(value_row))
            for cell, value in zip(cells, value_row):
                self.assertEqual(cell.text, value)
