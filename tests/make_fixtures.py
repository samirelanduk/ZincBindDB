import sys; sys.path += ["build", "core"]
import os
from unittest.mock import patch, Mock, MagicMock
from django.test import LiveServerTestCase
from django.core.management import call_command
from build.build import main as build_main
from build.cluster import main as cluster_main

class FixtureBuildingPretendTests(LiveServerTestCase):

    def setUp(self):
        self.patch1 = patch("build.build.get_zinc_pdb_codes")
        self.patch2 = patch("builtins.print")
        self.patch3 = patch("build.build.tqdm")
        self.patch4 = patch("build.cluster.tqdm")
        self.mock_codes = self.patch1.start()
        self.mock_print = self.patch2.start()
        self.mock_tqdm1 = self.patch3.start()
        self.mock_tqdm2 = self.patch4.start()
        self.mock_tqdm1.side_effect = lambda l: l
        self.mock_tqdm2.side_effect = lambda l: l
    

    def tearDown(self):
        self.patch1.stop()
        self.patch2.stop()
        self.patch3.stop()
        self.patch4.stop()
    

    def test_make_pre_cluster_fixtures(self):
        self.mock_codes.return_value = [
         "12CA", "1BNT", "1G48", # Carbonic anhydrase,
         "1MSO", "1XDA", "1IZB", # Insulin
         "1DEH", "3HUD", # Alcohol dehydrogenase
         "6ISO", "5Y5B" # Random
        ]
        build_main()
        with open("core/fixtures/pre-cluster.json", "w") as f:
            sysout, sys.stdout = sys.stdout, f
            call_command("dumpdata",  "--exclude=contenttypes", "--indent=2", verbosity=0)
        sys.stdout = sysout
    

    def test_make_post_cluster_fixtures(self):
        call_command("loaddata", "core/fixtures/pre-cluster.json")
        cluster_main()
        with open("core/fixtures/post-cluster.json", "w") as f:
            sysout, sys.stdout = sys.stdout, f
            call_command("dumpdata",  "--exclude=contenttypes", "--indent=2", verbosity=0)
        sys.stdout = sysout
