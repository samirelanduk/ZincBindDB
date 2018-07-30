#! /usr/bin/env python3

"""Examines the log produced by build_db.py"""

import sys
import os
from datetime import datetime
import re
from tqdm import tqdm
print("")

filename = ""
if len(sys.argv) < 2:
    filename = "data/logs/" + sorted(os.listdir("data/logs"))[-1]
else:
    filename = sys.argv[1]
with open(filename) as f:
    lines = f.read().splitlines()

pdb, pdbs = [], []
for line in lines:
    if "Getting PDB" in line:
        pdbs.append(pdb)
        pdb = []
    pdb.append(line)
pdbs.append(pdb)
pdbs.pop(0)

pdbs = [{
 "start": datetime.strptime(pdb[0].split(" - ")[0], "%Y-%m-%d %H:%M:%S,%f"),
 "lines": pdb,
 "pdb": pdb[0].split("Getting PDB ")[-1].split()[0]
} for pdb in pdbs]
for pdb1, pdb2 in zip(pdbs[:-1], pdbs[1:]):
    pdb1["end"] = pdb2["start"]
pdbs[-1]["end"] = datetime.strptime(pdbs[-1]["lines"][-1].split(" - ")[0], "%Y-%m-%d %H:%M:%S,%f")
for pdb in pdbs:
    pdb["duration"] = pdb["end"] - pdb["start"]
pdbs = list(reversed(sorted(pdbs, key=lambda p: p["duration"])))

for index, pdb in enumerate(pdbs[:5], start=1):
    print(index)
    print(pdb["pdb"], pdb["duration"])
    print()
print("")
