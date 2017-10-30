#! /usr/bin/env python3

import sys
import os
import django
sys.path.append(os.path.join("..", "zincbind"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zincbind.settings")
django.setup()
from zincbind.utilities import *
from zincbind.exceptions import RcsbError, AtomiumError
from zincbind.factories import create_empty_pdb, create_zinc_site


print("Fetching PDB codes...")
pdb_codes = get_all_pdb_codes()
print("There are {} current PDB codes.".format(len(pdb_codes)))

remove_checked_pdbs(pdb_codes)
print("There are {} which have never been checked.".format(len(pdb_codes)))

print("Checking PDBs...")
for code in pdb_codes:
    try:
        print("\tChecking {}...".format(code))
        if zinc_in_pdb(code):
            print("\tFound Zinc")
            pdb = get_pdb(code)
            model = pdb.model()
            for zinc in model.molecules(name="ZN"):
                site = zinc.site()
                create_zinc_site(pdb, zinc, site.residues())
                print("\t\tAdded {}".format(site))
        else:
            print("\tNo Zinc")
            create_empty_pdb(code)
    except RcsbError:
        print("Problem with {} RSCB".format(code))

    print("")
