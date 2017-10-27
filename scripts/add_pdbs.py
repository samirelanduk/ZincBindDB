#! /usr/bin/env python3

import sys
import os
import django
sys.path.append(os.path.join("..", "zincbind"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zincbind.settings")
django.setup()
from zincbind.utilities import *


print("Fetching PDB codes...")
pdb_codes = get_all_pdb_codes()
print("There are {} current PDB codes.".format(len(pdb_codes)))

remove_checked_pdbs(pdb_codes)
print("There are {} which have never been checked.".format(len(pdb_codes)))

print("Checking PDBs...")
for code in pdb_codes:
    print("\tChecking {}...".format(code))
    if zinc_in_pdb(code):
        print("\tFound Zinc")
    else:
        print("\tNo Zinc")
    print("")
