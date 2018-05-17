#! /usr/bin/env python3

"""When run, this script will build the ZincBind database from scratch."""

import sys
import os
sys.path.append(os.path.join("..", "zincbind"))
from zinc.utilities import get_zinc_pdb_codes

def main():
    # Get all PDBs which contain zinc
    codes = get_zinc_pdb_codes()
    print(f"There are {len(codes)} PDBs with zinc")


if __name__ == "__main__":
    main()
