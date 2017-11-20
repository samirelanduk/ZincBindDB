#! /usr/bin/env python3

import sys
import os
from atomium.structures import Residue
import django
sys.path.append(os.path.join("..", "zincbind"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zincbind.settings")
django.setup()
from zincbind.utilities import *
from zincbind.exceptions import RcsbError, AtomiumError
from zincbind.factories import create_empty_pdb, create_zinc_site


def main():
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
                if not model_is_skeleton(model):
                    for zinc in model.molecules(name="ZN"):
                        site = zinc.site(include_water=True)
                        if site.residues() and any(isinstance(res, Residue) for res in site.residues()):
                            create_zinc_site(pdb, zinc, site.residues())
                            print("\t\tAdded {}".format(site))
                        else:
                            print("\t\tNot adding {}".format(site))
                else:
                    print("\tDiscounting {} - skeleton PDB".format(code))
                    create_empty_pdb(code)
            else:
                print("\tNo Zinc")
                create_empty_pdb(code)
        except RcsbError:
            print("\tCould not obtain {} from RCSB".format(code))

        print("")

if __name__ == "__main__":
    main()
