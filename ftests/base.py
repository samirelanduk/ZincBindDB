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
        chain2 = Chain.objects.create(
         pdb=pdb1, id="A001B", sequence="MVTTYRLKSSSSWMDE", chain_pdb_identifier="B"
        )
        chain1 = Chain.objects.create(
         pdb=pdb1, id="A001A", sequence="MVTTYRLKSSSSWMDE", chain_pdb_identifier="A"
        )
        site1 = mixer.blend(ZincSite, pdb=pdb1, id="A0014003")
        site2 = mixer.blend(ZincSite, pdb=pdb1, id="A0018003")
        res1 = mixer.blend(
         Residue, site=site1, residue_pdb_identifier=23, insertion_pdb_identifier="", number=4, name="TYR", chain=chain1
        )
        res2 = mixer.blend(
         Residue, site=site1, residue_pdb_identifier=25, insertion_pdb_identifier="", number=3, name="VAL", chain=chain1
        )
        res3 = mixer.blend(
         Residue, site=site1, residue_pdb_identifier=21, insertion_pdb_identifier="", number=7, name="TYR", chain=chain1
        )
        res4 = mixer.blend(
         Residue, site=site2, residue_pdb_identifier=23, insertion_pdb_identifier="", number=4, name="TYR", chain=chain2
        )
        res5 = mixer.blend(
         Residue, site=site2, residue_pdb_identifier=25, insertion_pdb_identifier="", number=2, name="VAL", chain=chain2
        )
        res6 = mixer.blend(
         Residue, site=site2, residue_pdb_identifier=500, insertion_pdb_identifier="", number=0, name="HOH", chain=chain2
        )



        pdb2 = mixer.blend(
         Pdb, technique="NMR", resolution=0, rfactor=0, id="A002",
         title="A FINE PDB FILE", deposited=date(1992, 9, 28),
        )




    def tearDown(self):
        Pdb.objects.all().delete()
        self.browser.close()
