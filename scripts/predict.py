#! /usr/bin/env python3

"""When run, this script will look for binding sites in some file."""

import sys
import os
from pathlib import Path
sys.path.append(os.path.join("..", "zincbind"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
import django; django.setup()
from django.conf import settings
from itertools import combinations
import atomium

def print_and_log(log_path, string):
    with open(log_path, "a") as f:
        f.write(f"{string}\n\n")
    print(string)

# Where is the file?
try:
    file_path = sys.argv[1]
except:
    print("\nWhere is the file?\n")
    sys.exit()

# What is the folder?
folder = os.path.dirname(file_path) or os.getcwd()
log_path = f"{folder}/output.txt"

# Start log
print_and_log(log_path, "Starting job...")

# Open file
print_and_log(log_path, f"Opening {sys.argv[1].split('/')[-1]}...")
model = atomium.open(sys.argv[1]).model
print_and_log(log_path, f"Loaded {sys.argv[1].split('/')[-1]} - {len(model.atoms())} atoms")

# What profiles are there?
profiles = [f for f in os.listdir(settings.PROFILE_PATH) if f.endswith(".dat")]

# Use each profile in turn
for profile in profiles:
    print_and_log(log_path, f"Looking for {profile[:-4]} sites...")

    # Get residue combinations
    residues = []
    residue = []
    for char in profile:
        residue.append(char)
        if char.isdigit():
            residue[-1] = int(residue[-1])
            residues.append(residue)
            residue = []
    all_combos = []
    for residue in residues:
        all_residues = model.residues(code=residue[0])
        combos = list(combinations(all_residues, residue[1]))
        all_combos.append(combos)
    while len(all_combos) > 1:
         all_combos.insert(0, [(x,y) for x in all_combos[0] for y in all_combos[1]])
         all_combos.pop(1)
         all_combos.pop(1)
    all_combos = all_combos[0]
    if isinstance(all_combos[0][0], tuple): all_combos = [r[0] for r in all_combos]
    print_and_log(log_path, f"\t{len(all_combos)} possible combinations...")
