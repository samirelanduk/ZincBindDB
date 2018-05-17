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

        Pdb.objects.create(
         id="A001", title="A SUPERB PDB", deposited=date(1990, 9, 28),
         resolution=2.1, organism="FELIS CATUS", expression="MUS MUSCULUS",
         classification="REDUCTASE", technique="X-RAY", skeleton=False,
         rfactor=4.5
        )


    def tearDown(self):
        self.browser.close()
