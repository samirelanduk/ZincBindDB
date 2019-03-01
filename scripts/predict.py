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
import numpy as np

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

try:
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
            print_and_log(log_path, f"\tThere are {len(all_residues)} {residue[0]} residues")
            combos = list(combinations(all_residues, residue[1]))
            all_combos.append(combos)
        while len(all_combos) > 1:
             all_combos.insert(0, [(x,y) for x in all_combos[0] for y in all_combos[1]])
             all_combos.pop(1)
             all_combos.pop(1)
        all_combos = all_combos[0]
        if all_combos and isinstance(all_combos[0][0], tuple): all_combos = [r[0] for r in all_combos]
        print_and_log(log_path, f"\t{len(all_combos)} possible combinations...")

        # Create vectors
        vectors = {}
        print_and_log(log_path, "\tCreating vectors...")
        for combo in all_combos:
            res1, res2 = combo
            dist1 = round(res1.atom(name="CA").distance_to(res2.atom(name="CA")), 3)
            dist2 = round(res1.atom(name="CB").distance_to(res2.atom(name="CB")), 3)
            vectors[combo] = [dist1, dist2]

        # Load energy landscape
        with open(settings.PROFILE_PATH + "/" + profile) as f:
            lines = f.read().splitlines()
            grid = eval(lines[0])
            X = eval(lines[2])
            Y = eval(lines[4])

        # Evaluate potential sites in turn
        scores = {}
        for combo, vector in vectors.items():
            for x in range(len(X) - 1):
                for y in range(len(Y) - 1):
                    if X[x] < vector[0] < X[x + 1] and Y[y] < vector[1] < Y[y + 1]:
                        scores[combo] = grid[x][y]
                        break
            if combo not in scores: scores[combo] = np.inf
        for combo, score in sorted(scores.items(), key=lambda s: s[1]):
            print_and_log(log_path, f"{str(combo[0])[9:-1]}, {str(combo[1])[9:-1]} {score} {vectors[combo]}")
except Exception as e:
    print_and_log(log_path, str(e))
