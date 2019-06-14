import sys; sys.path += ["build", "core"]
from unittest.mock import patch, Mock, MagicMock
from django.test import LiveServerTestCase
from django.core.management import call_command
from build import main

class DatabaseBuildingTests(LiveServerTestCase):

    def setUp(self):
        self.patch1 = patch("build.get_zinc_pdb_codes")
        self.patch2 = patch("builtins.print")
        self.patch3 = patch("build.tqdm")
        self.mock_codes = self.patch1.start()
        self.mock_print = self.patch2.start()
        self.mock_tqdm = self.patch3.start()
        self.mock_tqdm.side_effect = lambda l: l
    

    def test_make_pre_cluster_fixtures(self):
        self.mock_codes.return_value = [
         "12CA", "1BNT", "1G48", # Carbonic anhydrase,
         "1MSO", "1XDA", "1IZB", # Insulin
         "1DEH", "3HUD", # Alcohol dehydrogenase
         "6ISO", "5Y5B" # Random
        ]
        main()
        with open("core/fixtures/pre-cluster.json", "w") as f:
            sysout, sys.stdout = sys.stdout, f
            call_command("dumpdata",  "--exclude=contenttypes", verbosity=0)
        sys.stdout = sysout

import unittest
unittest.main()