#! /usr/bin/env python3

"""When run, this script will build profiles of site families."""

import sys
import os
sys.path.append(os.path.join("..", "zincbind"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
import django; django.setup()
from core.models import *
from tqdm import tqdm
from itertools import combinations
import numpy as np
import matplotlib.pyplot as plt

FAMILIES = ["E2"]

for family in FAMILIES:
    print(f"Creating profile for {family} sites.")

    # Get all relevant binding sites
    sites = ZincSite.objects.filter(family=family, pdb__resolution__lt=2.5)
    print(f"  There are {sites.count()} sites to process.")

    profiles = []
    for site in sites:
        # Only use residues on a chain, not ligands
        residues = Residue.objects.filter(site=site).exclude(chain=None)

        # Create combinations
        combos = list(combinations(residues, 2))

        # Make profile
        profile = []
        for combo in combos:
            res1, res2 = combo
            profile.append(round(
             res1.atom_set.get(name="CA").distance_to(res2.atom_set.get(name="CA")), 3
            ))
            profile.append(round(
             res1.atom_set.get(name="CB").distance_to(res2.atom_set.get(name="CB")), 3
            ))
        profiles.append(profile)

    # Distribution
    bins = sites.count() / 10
    alphas, betas = zip(*profiles)
    hist, x, y = np.histogram2d(alphas, betas, bins=bins)
    average = lambda c: sum(c) / len(c)
    average_count = average([average(row) for row in hist])
    #print(average_count)
    #print(hist)
    hist = [[round(-np.log(val / average_count), 3) for val in row] for row in hist]
    #print(hist)
    plt.imshow(hist, interpolation='nearest', origin='low', extent=[x[0], x[-1], y[0], y[-1]])
    #plt.show()

    data = f"{hist}\n\n{list(x)}\n\n{list(y)}".replace("inf", "np.inf")
    with open(f"data/profiles/{family}.dat", "w") as f:
        f.write(data)
