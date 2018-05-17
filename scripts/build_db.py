#! /usr/bin/env python3

"""When run, this script will build the ZincBind database from scratch."""

import sys
import os
sys.path.append(os.path.join("..", "zincbind"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
import django; django.setup()
from zinc.utilities import get_zinc_pdb_codes
from zinc.models import *
import atomium
from tqdm import tqdm

def main():
    # Get all PDBs which contain zinc
    codes = get_zinc_pdb_codes()
    print(f"There are {len(codes)} PDBs with zinc")

    # Go through each PDB
    for code in tqdm(codes):
        pdb = atomium.fetch(code, pdbe=True)
        pdb_record = Pdb.create_from_atomium(pdb)
        for chain in pdb.model.chains():
            Chain.create_from_atomium(chain, pdb_record)
        for zinc in pdb.model.atoms(element="ZN"):
            Zinc.create_from_atomium(zinc, pdb_record)

if __name__ == "__main__":
    main()
