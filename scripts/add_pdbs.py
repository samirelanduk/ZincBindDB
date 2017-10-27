#! /usr/bin/env python3

import sys
import os
sys.path.append(os.path.join("..", "zincbind"))
from zincbind.utilities import *

pdb_codes = get_all_pdb_codes()
print("There are {} current PDB codes.".format(len(pdb_codes)))
