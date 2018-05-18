import os
from datetime import date
from selenium import webdriver
from testarsenal import BrowserTest
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from zinc.models import *

class FunctionalTest(StaticLiveServerTestCase, BrowserTest):

    def setUp(self):
        self.headless = os.environ.get("djangovar") == "headless"
        if self.headless:
            self.browser = webdriver.PhantomJS()
        else:
            self.browser = webdriver.Chrome()

        pdb = Pdb.objects.create(
         id="A001", title="A SUPERB PDB", deposited=date(1990, 9, 28),
         resolution=2.1, organism="FELIS CATUS", skeleton=False,
         expression="ESCHERICHIA COLI BL21(DE3)", rfactor=4.5,
         classification="REDUCTASE", technique="X-RAY",
        )
        Zinc.objects.create(id="A001456", x=1.4, y=-0.9, z=120, pdb=pdb)
        Zinc.objects.create(id="A001458", x=10.4, y=-1.9, z=1.2, pdb=pdb)


    def tearDown(self):
        self.browser.close()
