import os
from datetime import date
from selenium import webdriver
from mixer.backend.django import mixer
from testarsenal import BrowserTest
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.management import call_command
from core.models import *

class FunctionalTest(StaticLiveServerTestCase, BrowserTest):

    def setUp(self):
        self.headless = os.environ.get("djangovar") == "headless"
        if self.headless:
            self.browser = webdriver.PhantomJS()
        else:
            self.browser = webdriver.Chrome()

        call_command(
         "loaddata", "ftests/testdb.json", "--exclude=contenttypes", verbosity=0
        )
        # 6EQU (1 site)
        # 1B21 (1 site)
        # 4UXY (0 sites)
        # 6H8P (? site)
        # 1ZEH (2 sites)
        # 1A6F (2 sites)
        # 1BYF (? sites)
        # 1A0Q (? sites)


    def tearDown(self):
        Pdb.objects.all().delete()
        self.browser.close()
