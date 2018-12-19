#! /usr/bin/env python3

"""When run, this script will report useful stats on the ZincBind database."""

import sys
import os
import requests
import json
import numpy as np
from scipy.stats import fisher_exact
import matplotlib.pyplot as plt
from itertools import groupby
sys.path.append(os.path.join("..", "zincbind"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
import django; django.setup()
from django.db.models import Count, F
from core.models import *

print()
BOLD = "\033[1m"
END = "\033[0m"
FAIL = "\033[91m"

# ZINC PREVALENCE
zinc_pdb_count = Pdb.objects.count()
latest_date = Pdb.objects.latest("deposited").deposited
r = requests.post("https://www.rcsb.org/pdb/search/smartRow.do",
 headers={"Content-Type": "application/x-www-form-urlencoded"},
 data={"smartSearchSubtype": "ReleaseDateQuery", "r": "0", "target": "Current",
  "pdbx_audit_revision_history.revision_date.comparator": "between",
  "pdbx_audit_revision_history.revision_date.max": latest_date,
  })
pdb_count = int(r.text.split("'")[1].split()[0])
proportion = (zinc_pdb_count / pdb_count) * 100

print(f"{BOLD}Prevalence of Zinc{END}")
print(f"There are {zinc_pdb_count} PDBs with zinc in")
print(f"There were {pdb_count} PDBs on {latest_date}")
print(f"Zinc is therefore found in {proportion:.2f}% of PDBs")
print()

# METAL DISTRIBUTION
metals = Metal.objects.all()
metal_count = metals.count()
zinc_count = metals.filter(element="ZN").count()
non_zinc = metals.exclude(element="ZN").count()
z_prop = (zinc_count / metal_count) * 100
nz_prop = (non_zinc / metal_count) * 100
non_zinc_counts = Counter([m.element for m in metals.exclude(element="ZN")])

print(f"{BOLD}Distribution of Metals{END}")
print(f"There are {zinc_count} zinc atoms in the PDB")
print(f"These are associated with {non_zinc} other metals")
print(f"This is a total of {metal_count} metals - {z_prop:.2f}% zinc and {nz_prop:.2f}% non-zinc")
print("The non-zinc metals are:")
for key, value in non_zinc_counts.most_common(10):
    print(f"    {key}: {value} ({(value / non_zinc) * 100:.2f}%)")
print()


# METAL EXCLUSION
zincs_with_site = Metal.objects.filter(element="ZN").exclude(site=None).count()
zincs_without_site = Metal.objects.filter(element="ZN", site=None).count()
zincs_with_site_prop = (zincs_with_site / zinc_count) * 100
zincs_without_site_prop = (zincs_without_site / zinc_count) * 100
exclusion_reasons = Counter([z.omission for z in Metal.objects.filter(element="ZN", site=None)])

print(f"{BOLD}Exclusion of Zinc{END}")
print(f"There are {zinc_count} zinc atoms")
print(f"{zincs_with_site} have a binding site associated {zincs_with_site_prop:.2f}%")
print(f"{zincs_without_site} have no binding site associated {zincs_without_site_prop:.2f}%")
print("Reasons for exclusion:")
for key, value in exclusion_reasons.most_common(10):
    print(f"    {value} ({(value / zincs_without_site) * 100:.2f}%): {key}")
print()


# EQUIVALENT SITES
metals_with_site = Metal.objects.exclude(site=None).count()
site_count = ZincSite.objects.count()
unique_count = ZincSite.objects.filter(representative=True).count()
clusters = ZincSiteCluster.objects.annotate(count=Count('zincsite'))
top_three_clusters = sorted(clusters, key=lambda c: c.count)[::-1][:3]
lone_count = len([c for c in clusters if c.count == 1])

print(f"{BOLD}Equivalent Sites{END}")
print(f"{metals_with_site} metals are distributed among {site_count} sites")
print(f"That's an average of {(metals_with_site / site_count):.2f} metals per site")
print(f"These sites represent {unique_count} sites")
print("Top three clusters by number of representatives:")
for cluster in top_three_clusters:
    print(f"    {cluster.zincsite_set.first().id} ({cluster.count})")
print(f"{lone_count} clusters have only one member ({(lone_count / unique_count) * 100:.2f}%)")
print()


# LIGANDING RESIDUES
for unique in (False, True):
    residues = Residue.objects.filter(site__representative=True) if unique else Residue.objects.all()
    residue_count = residues.count()
    top_five = Counter([r.name for r in residues]).most_common(5)
    top_five_count = sum([n[1] for n in top_five])
    sites = ZincSite.objects.filter(representative=True) if unique else ZincSite.objects.all()
    common_codes = Counter([site.code for site in sites]).most_common(10)
    top_ten_code_count = sum([n[1] for n in common_codes])

    print(f"{BOLD}Liganding Residues{' (unique)' if unique else ''}{END}")
    print(f"There are {residue_count}{' unique' if unique else ''} liganding residues")
    print(f"{top_five_count} ({(top_five_count / residue_count) * 100:.2f}%) of these come from the top-five:")
    for res, count in top_five:
        print(f"    {res}: {count} ({(count / residue_count) * 100:.2f}%)")
    print(f"The most common site code is {common_codes[0][0]}, with {common_codes[0][1]} ({(common_codes[0][1] / sites.count()) * 100:.2f}%)")
    print(f"The top ten codes account for {top_ten_code_count} sites ({(top_ten_code_count / sites.count()) * 100:.2f}%)")
    print()


# LIGANDING ATOMS
sites = ZincSite.objects.annotate(metal_count=Count("metal"), classification=F("pdb__classification"))
mononuclear = [s for s in sites if s.metal_count == 1]
liganding_atoms = Atom.objects.filter(liganding=True).annotate(site=F("residue__site"), metal_count=Count("residue__site__metal"))
liganding_atoms = [a for a in liganding_atoms if a.metal_count == 1]
liganding_atoms = sorted(liganding_atoms, key=lambda a: a.site)
groups = groupby(liganding_atoms, key=lambda a: a.site)
groups = [{"site": site, "atoms": list(atoms)} for site, atoms in groups]
coordination_numbers = Counter([len(g["atoms"]) for g in groups])
top_coord = coordination_numbers.most_common(1)[0]
coordinations = coordination_numbers.most_common(4)
other_coords = len(mononuclear) - sum(c[1] for c in coordinations)
try:
    with open("data/distances.json") as f:
        distance_json = json.load(f)
    dist_data = []
    for element in "ONS":
        distances = [a["distance"] for a in distance_json if a["element"] == element]
        mean = sum(distances) / len(distances)
        sd = np.std(distances)
        dist_data.append([element, mean, sd])
except:
    print(f"{FAIL}Couldn't process distances{END}")

print(f"{BOLD}Liganding Atoms{END}")
print(f"There are {len(mononuclear)} sites with one metal")
print(f"The most common coordination is {top_coord[0]} - {top_coord[1]} ({(top_coord[1] / len(mononuclear)) * 100:.2f}%)")
print("All coordination modes:")
for coord in sorted(coordinations, key=lambda c: c[0]):
    print(f"    {coord[0]}: {coord[1]} ({(coord[1] / len(mononuclear)) * 100:.2f}%)")
print(f"    Other: {other_coords} ({(other_coords / len(mononuclear)) * 100:.2f}%)")
try:
    for element in dist_data:
        print(f"Average {element[0]} distance: {element[1]:.2f} (+/- {element[2]:.2f})")
except: pass
print()


# POLYNUCLEAR SITES
polynuclear = [s for s in sites if s.metal_count > 1]
metal_counts = Counter([s.metal_count for s in polynuclear]).most_common(5)
other_counts = len(polynuclear) - sum(c[1] for c in metal_counts)
poly_enzymes = [s for s in polynuclear if "ase" in s.classification.lower()]
mono_enzymes = [s for s in mononuclear if "ase" in s.classification.lower()]
odds, sig = fisher_exact([
 [len(mono_enzymes), len(mononuclear) - len(mono_enzymes)],
 [len(poly_enzymes), len(polynuclear) - len(poly_enzymes)]
])

print(f"{BOLD}Coactive Sites{END}")
print(f"There are {len(mononuclear)} sites with one metal ({(len(mononuclear) / site_count) * 100:.2f}%)")
print(f"There are {len(polynuclear)} sites with multiple metals ({(len(polynuclear) / site_count) * 100:.2f}%):")
for count, count_count in metal_counts:
    print(f"    {count_count} sites have {count} metals ({(count_count / len(polynuclear)) * 100:.2f}%)")
print(f"    {other_counts} sites have more metals ({(other_counts / len(polynuclear)) * 100:.2f}%)")
print(f"{len(poly_enzymes)} polynuclear sites are enzymes ({(len(poly_enzymes) / len(polynuclear)) * 100:.2f}%)")
print(f"{len(mono_enzymes)} mononuclear sites are enzymes ({(len(mono_enzymes) / len(mononuclear)) * 100:.2f}%)")
print(f"The p-value for this significance is {sig}")
print()


# CHARTS
print("Outputting charts...")

plt.bar(range(1, 101), [c.count for c in sorted(clusters, key=lambda c: c.count)[::-1][:100]], width=1, color="#4A9586")
plt.xlabel("ZincSite Cluster"), plt.ylabel("Number of Representatives")
name = "site-representatives.eps"; plt.savefig(name); plt.clf()
print(f"    Saved {name}")

STEP = 0.01
def make_histogram_data(j, element=None):
    distances = [a["distance"] for a in j if not element or a["element"] == element]
    bins = {round(x * STEP, 2): [] for x in range(int(3 * (1 / STEP)))}
    for d in distances:
        for cutoff in reversed(sorted(bins.keys())):
            if d > cutoff:
                bins[cutoff].append(d)
                break
    bins = {x: len(y) for x, y in bins.items()}
    return zip(*bins.items())
x, y = make_histogram_data(distance_json)
xo, yo = make_histogram_data(distance_json, element="O")
xn, yn = make_histogram_data(distance_json, element="N")
xs, ys = make_histogram_data(distance_json, element="S")
params = {"width": STEP, "align": "edge"}
f, axarr = plt.subplots(2, 2)
axarr[0, 0].bar(x, y, label="All atoms", color="#4A9586", **params)
axarr[0, 0].set_xlim([1, 3]), axarr[0, 0].set_ylim([0, 2500]), axarr[0, 0].set_ylabel("Count"), axarr[0, 0].legend()
axarr[0, 1].bar(x, y, label="All atoms", color="#a4cac2", **params)
axarr[0, 1].bar(xo, yo, label="Oxygen", color="#ff4757", **params)
axarr[0, 1].set_xlim([1, 3]), axarr[0, 1].set_ylim([0, 2500]), axarr[0, 1].legend()
axarr[1, 0].bar(x, y, label="All atoms", color="#a4cac2", **params)
axarr[1, 0].bar(xn, yn, label="Nitrogen", color="#1e90ff", **params)
axarr[1, 0].set_xlim([1, 3]), axarr[1, 0].set_ylim([0, 2500]), axarr[1, 0].set_xlabel("Metal-Ligand Distance (Å)"), axarr[1, 0].set_ylabel("Count"), axarr[1, 0].legend()
axarr[1, 1].bar(x, y, label="All atoms", color="#a4cac2", **params)
axarr[1, 1].bar(xs, ys, label="Sulphur", color="#fbc531", **params)
axarr[1, 1].set_xlim([1, 3]), axarr[1, 1].set_ylim([0, 2500]), axarr[1, 1].set_xlabel("Metal-Ligand Distance (Å)"), axarr[1, 1].legend()
f.subplots_adjust(wspace=0.3, hspace=0.3)
for ext in ["png", "eps"]:
    name = "atom-distances." + ext; f.savefig(name)
    print(f"    Saved {name}")
plt.clf()

print()
