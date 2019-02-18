#! /usr/bin/env python3

"""When run, this script will build profiles of site families."""

import sys
import os
sys.path.append(os.path.join("..", "zincbind"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
import django; django.setup()
from core.models import *
from tqdm import tqdm

FAMILIES = ["E2"]

for family in FAMILIES:
    print(f"Creating profile for {family} sites.")

    # Get all relevant binding sites
    sites = ZincSite.objects.filter(family=family, pdb__resolution__lt=2.5)
    print(f"  There are {sites.count()} sites to process.")
