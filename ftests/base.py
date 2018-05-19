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
         id="A001", title="A SUPERB PDB FILE", deposited=date(1990, 9, 28),
         resolution=2.1, organism="FELIS CATUS", skeleton=False,
         expression="ESCHERICHIA COLI BL21(DE3)", rfactor=4.5,
         classification="REDUCTASE", technique="X-RAY",
        )
        pdb = Pdb.objects.create(
         id="A002", title="A FINE PDB FILE", deposited=date(1992, 9, 28),
         resolution=2.4, organism="HOMO SAPIENS", skeleton=False,
         expression="ESCHERICHIA COLI", rfactor=4.8,
         classification="TRANSFERASE", technique="X-RAY",
        )
        pdb = Pdb.objects.create(
         id="B123", title="A MESS OF ATOMS", deposited=date(2002, 7, 28),
         resolution=2.5, organism="FELIS CATUS", skeleton=False,
         expression="ESCHERICHIA COLI", rfactor=2.5,
         classification="REDUCTASE", technique="X-RAY",
        )


    def tearDown(self):
        Pdb.objects.all().delete()
        self.browser.close()
