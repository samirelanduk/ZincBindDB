#! /usr/bin/env python3

"""When run, this script will build profiles of site families."""

import sys
import os
import warnings
sys.path.append(os.path.join("..", "zincbind"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
import django; django.setup()
from core.models import *
from tqdm import tqdm
from itertools import combinations
import numpy as np
import matplotlib.pyplot as plt

warnings.simplefilter("ignore")

def smooth_matrix(matrix):
    new_matrix = [[0 for val in row] for row in matrix]
    for r in range(len(matrix)):
        for c in range(len(matrix[0])):
            values = []
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    nr = r + dr
                    nc = c + dc
                    if (0 <= nr < len(matrix)) and (0 <= nc < len(matrix[0])):
                        val = matrix[r + dr][c + dc]
                        values.append(val)
            new_matrix[r][c] = sum(v for v in values if v!=-np.inf) / len(values) if any(v != -np.inf for v in values) else -np.inf
    return new_matrix

FAMILIES = ["E2", "H3"]

for family in FAMILIES:
    print(f"Creating profile for {family} sites.")

    # Get all relevant binding sites
    sites = ZincSite.objects.filter(family=family, pdb__resolution__lt=2.5)
    print(f"  There are {sites.count()} sites to process.")

    profiles = []
    for site in tqdm(sites):
        # Only use residues on a chain, not ligands
        residues = Residue.objects.filter(site=site).exclude(chain=None)

        # Create combinations
        combos = list(combinations(residues, 2))

        # Make profile
        CAs, CBs = [], []
        for combo in combos:
            res1, res2 = combo
            CAs.append(round(
             res1.atom_set.get(name="CA").distance_to(res2.atom_set.get(name="CA")), 3
            ))
            CBs.append(round(
             res1.atom_set.get(name="CB").distance_to(res2.atom_set.get(name="CB")), 3
            ))
        profile = [
         sum(CAs) / len(CAs), sum(CBs) / len(CBs)
        ]
        profiles.append(profile)

    # Distribution
    print("  Processing")
    bins = sites.count() / 10
    alphas, betas = zip(*profiles)
    hist, x, y = np.histogram2d(alphas, betas, bins=bins)
    average = lambda c: sum(c) / len(c)
    average_count = average([average(row) for row in hist])
    hist = [[round(np.log(val / average_count), 3) for val in row] for row in hist]
    plt.imshow([[val if val != -np.inf else 0 for val in row] for row in hist], interpolation='nearest', origin='low', extent=[x[0], x[-1], y[0], y[-1]])
    plt.colorbar()
    plt.savefig(f"data/profiles/{family}.png")
    ax = plt.gca()
    ax.set_facecolor("b")
    plt.clf()

    data = f"{hist}\n\n{list(x)}\n\n{list(y)}".replace("inf", "np.inf")
    with open(f"data/profiles/{family}.dat", "w") as f:
        f.write(data)


    # Again, but smoothed
    hist = smooth_matrix(hist)
    hist = smooth_matrix(hist)
    hist = smooth_matrix(hist)
    plt.imshow([[val if val != -np.inf else 0 for val in row] for row in hist], interpolation='nearest', origin='low', extent=[x[0], x[-1], y[0], y[-1]])
    plt.colorbar()
    plt.savefig(f"data/profiles/{family}_smooth.png")
    plt.clf()

    data = f"{hist}\n\n{list(x)}\n\n{list(y)}".replace("inf", "np.inf")
    with open(f"data/profiles/{family}_smooth.dat", "w") as f:
        f.write(data)
