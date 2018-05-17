#! /usr/bin/env python3

"""When run, this script will build the ZincBind database from scratch."""

import sys
import os
sys.path.append(os.path.join("..", "zincbind"))
import django
sys.path.append(os.path.join("..", "zincbind"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()
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
        Pdb.create_from_atomium(pdb)


if __name__ == "__main__":
    main()
