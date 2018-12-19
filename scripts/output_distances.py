#! /usr/bin/env python3

"""When run, this script will produce a JSON file of ligand distances."""

import sys
import os
import matplotlib.pyplot as plt
sys.path.append(os.path.join("..", "zincbind"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
import django; django.setup()
from django.db.models import Count
from core.models import *
from tqdm import tqdm
import numpy as np
import json

def distance(a, b):
    x1, y1, z1 = a.x, a.y, a.z
    x2, y2, z2 = b.x, b.y, b.z

    x_sum = pow((x1 - x2), 2)
    y_sum = pow((y1 - y2), 2)
    z_sum = pow((z1 - z2), 2)
    return np.sqrt(x_sum + y_sum + z_sum)

sites = ZincSite.objects.exclude(pdb__resolution__gt=3).annotate(metals=Count('metal'))
print(f"There are {sites.count()} sites with resolution better than 3A")

atoms = []
for site in tqdm(sites):
    if site.metals == 1:
        metal = Metal.objects.get(site=site)
        ligands = Atom.objects.filter(residue__site=site, liganding=True)
        for atom in ligands:
            atoms.append({
             "name": atom.name, "element": atom.element,
             "distance": distance(atom, metal)
            })

with open("data/distances.json", "w") as f:
    json.dump(atoms, f)
