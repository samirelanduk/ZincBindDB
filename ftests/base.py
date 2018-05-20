import os
from datetime import date
from selenium import webdriver
from mixer.backend.django import mixer
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

        pdb1 = Pdb.objects.create(
         id="A001", title="A SUPERB PDB FILE", deposited=date(1990, 9, 28),
         resolution=2.1, organism="FELIS CATUS", skeleton=False,
         expression="ESCHERICHIA COLI BL21(DE3)", rfactor=4.5,
         classification="REDUCTASE", technique="X-RAY",
        )
        chain1 = Chain.objects.create(
         pdb=pdb1, id="A001B", sequence="MVTTYRLKSSSSWMDE"
        )
        chain2 = Chain.objects.create(
         pdb=pdb1, id="A001A", sequence="MVTTYRLKSSSSWMDE"
        )
        site1 = mixer.blend(ZincSite, pdb=pdb1, id="A0014003")
        site2 = mixer.blend(ZincSite, pdb=pdb1, id="A0018003")
        res1 = mixer.blend(
         Residue, site=site1, residue_id="A23", number=4, name="TYR"
        )
        res2 = mixer.blend(
         Residue, site=site1, residue_id="A25", number=3, name="VAL"
        )
        res3 = mixer.blend(
         Residue, site=site1, residue_id="A21", number=7, name="TYR"
        )
        res4 = mixer.blend(
         Residue, site=site2, residue_id="B23", number=4, name="TYR"
        )
        res5 = mixer.blend(
         Residue, site=site2, residue_id="B25", number=2, name="VAL"
        )
        res6 = mixer.blend(
         Residue, site=site2, residue_id="B500", number=0, name="HOH"
        )



        pdb2 = mixer.blend(
         Pdb, technique="NMR", resolution=0, rfactor=0, id="A002",
         title="A FINE PDB FILE", deposited=date(1992, 9, 28),
        )




    def tearDown(self):
        Pdb.objects.all().delete()
        self.browser.close()
