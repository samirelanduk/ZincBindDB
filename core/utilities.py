import requests
import logging
import time
import os
import sys
import math
from datetime import datetime
from atomium.data import CODES
from itertools import combinations
from atomium.structures import Chain, Residue
from django.core.management import call_command
from core.models import Pdb

CODES = CODES.copy()
CODES["HOH"] = "w"

def get_zinc_pdb_codes():
    """Gets PDB codes for all structures with a zinc atom in them.

    If the response returned has an error code of 500, or if there are fewer
    than 10,000 PDB codes sent back, an RcsbError will be thrown."""

    query = "<orgPdbQuery>"\
    "<queryType>org.pdb.query.simple.ChemCompFormulaQuery</queryType>"\
    "<formula>ZN</formula></orgPdbQuery>"
    url = "https://www.rcsb.org//pdb/rest/search/"
    response = requests.post(url, data=query.encode(), headers={
     "Content-Type": "application/x-www-form-urlencoded"
    })
    if response.status_code == 200:
        codes = response.text.split()
        if len(codes) > 10000:
            return response.text.split()
    raise Exception("RCSB didn't send back PDB codes")


def remove_checked_codes(codes):
    checked = [p.id for p in Pdb.objects.all()]
    return [c for c in codes if c not in checked]


def get_best_model(pdb):
    assemblies = sorted(pdb.assemblies, key=lambda a: math.inf
     if a["delta_energy"] is None else a["delta_energy"])
    if assemblies:
        model = pdb.generate_assembly(assemblies[0]["id"])
        metals = model.atoms(is_metal=True)
        while not metals:
            assemblies.pop(0)
            model = pdb.generate_assembly(assemblies[0]["id"])
            metals = model.atoms(is_metal=True)
        return model, assemblies[0]["id"]
    else:
        return pdb.model, None


def model_is_skeleton(model):
    """Returns ``True`` if the model given only contains backbone atoms."""

    for residue in model.residues():
        atom_names = set([atom.name for atom in residue.atoms()])
        for name in atom_names:
            if name not in ["C", "N", "CA", "O"]:
                return False
    return True


def zincs_outside_model(model, pdb):
    au_zincs = pdb.model.atoms(element="ZN")
    assembly_zinc_ids = [atom.id for atom in model.atoms(element="ZN")]
    return [z for z in au_zincs if z.id not in assembly_zinc_ids]



def cluster_zincs_with_residues(metals):
    """This function takes a set of atoms - all the metal atoms found in an
    atomium model.

    For each atom it will identify the binding residues for that atom and
    associate them with each other.

    From this dictionary, a list of cluster dictionaries will be made. In the
    simplest case, each metal will be a cluster, but two metal atoms will be
    merged into one cluster if they share binding residues.

    Then, duplicates will be removed. Two clusters are duplicates if they have
    the same metal atom IDs - this is usually created from symmetry operations.

    Finally clusters with no zinc in are removed."""

    metals = remove_duplicate_atoms(metals)
    metals = {metal: [] for metal in metals}
    for metal in metals:
        metals[metal] = get_atom_binding_residues(metal)
    clusters = merge_metal_groups(metals)
    aggregate_clusters(clusters)
    return [c for c in clusters if "ZN" in [a.element for a in c["metals"]]]


def remove_duplicate_atoms(atoms):
    new_set = set()
    elements = set([m.element for m in atoms])
    for element in elements:
        relevant_atoms = [m for m in atoms if m.element == element]
        unique_relevant = set()
        for r in relevant_atoms:
            for u in unique_relevant:
                if r.distance_to(u) < 1:
                    break
            else:
                unique_relevant.add(r)
        new_set.update(unique_relevant)
    return new_set


def get_atom_binding_residues(metal):
    """Takes an atom and gets all residues within 3Å - including ligands.
    In the case of zinc atoms, it will only use nitrogen, oxygen or sulphur
    atoms. For other atoms it will take everything except carbons.

    It will also mark atoms as 'liganding' or otherwise."""

    kwargs = {"cutoff": 3, "is_metal": False}
    nearby_atoms = [a for a in metal.nearby_atoms(**kwargs) if a.element not in "CH"]
    nearby_residues = set([a.structure for a in nearby_atoms])
    nearby_residues = remove_duplicate_residues(nearby_residues)
    for residue in nearby_residues:
        liganding = [a for a in residue.atoms() if a in nearby_atoms]
        liganding = sorted(liganding, key=lambda a: a.distance_to(metal))
        if liganding:
            liganding = [liganding[0]] + [a for a in liganding[1:] if metal.angle(liganding[0], a) > math.pi / 4]
        for atom in residue.atoms(): atom._flag = False
        for atom in liganding: atom._flag = True
    return nearby_residues


def remove_duplicate_residues(residues):
    molecules = [r for r in residues if len(r.atoms()) > 1]
    atoms = {r.atom(): r for r in residues if len(r.atoms()) == 1}
    unique_atoms = remove_duplicate_atoms(atoms.keys())
    for atom in unique_atoms:
        molecules.append(atoms[atom])
    return set(molecules)


def merge_metal_groups(metals):
    """Takes a dictionary in which the keys are metal atoms and the values are
    the set of residues that bind to them.

    It then creates a list of clusters from this, where each cluster is a dict
    object with metals and residues. Two metals and their residues will be
    merged together if they share residues."""

    clusters = [{"metals": {metal}, "residues": residues, "count": 1}
     for metal, residues in metals.items()]
    while not check_clusters_have_unique_residues(clusters):
        for cluster1, cluster2 in combinations(clusters, 2):
            if cluster1["residues"].intersection(cluster2["residues"]):
                cluster1["metals"].update(cluster2["metals"])
                cluster1["residues"].update(cluster2["residues"])
                clusters.remove(cluster2)
                break
    return clusters


def check_clusters_have_unique_residues(clusters):
    """Takes a list of clusters and returns True if they don't share any
    residues in common."""

    residue_count = sum([len(cluster["residues"]) for cluster in clusters])
    unique_residue_count = len(set.union(
     *[cluster["residues"] for cluster in clusters]
    ))
    return residue_count == unique_residue_count


def remove_duplicates_from_cluster(cluster):
    """Takes a cluster representing a binding site, and removes a metal if its
    ID is duplicated in the cluster."""

    identifiers = set([m.id for m in cluster["metals"]])
    new_metals = set()
    for id_ in identifiers:
        for metal in cluster["metals"]:
            if metal.id == id_:
                new_metals.add(metal)
                break
    cluster["metals"] = new_metals
    new_residues, potential_residues = set(), set()
    for residue in cluster["residues"]:
        if len(residue.atoms()) > 1:
            new_residues.add(residue)
        else:
            potential_residues.add(residue)
    locations = set([(r.atom().location) for r in potential_residues])
    for loc in locations:
        for residue in potential_residues:
            if residue.atom().location == loc:
                new_residues.add(residue)
                break
    cluster["residues"] = new_residues


def aggregate_clusters(clusters):
    """Takes a list of cluster dictionaries and merges those with the same metal
    IDs."""

    while not check_clusters_have_unique_sites(clusters):
        for cluster1, cluster2 in combinations(clusters, 2):
            if set([m.id for m in cluster1["metals"]]) ==\
             set([m.id for m in cluster2["metals"]]):
                cluster1["count"] += 1
                clusters.remove(cluster2)
                break


def check_clusters_have_unique_sites(clusters):
    """Takes a list of clusters and returns True if they have any equivalent
    sites."""

    cluster_ids = [frozenset([
     m.id for m in cluster["metals"]
    ]) for cluster in clusters]
    unique_ids = set(cluster_ids)
    return len(cluster_ids) == len(unique_ids)


def create_chains_dict(clusters):
    chains = {}
    for cluster in clusters:
        for o in cluster["residues"]:
            chains[o.chain.id] = o.chain
    return chains


def residue_count(cluster):
    return len([r for r in cluster["residues"] if isinstance(r, Residue)])


def liganding_atom_count(cluster):
    atoms = []
    for residue in cluster["residues"]:
        atoms += [a for a in residue.atoms() if a._flag]
    return len(atoms)


def create_site_code(residues):
    codes = [CODES.get(r.name, "X") for r in residues if r.__class__.__name__ == "Residue"]
    return "".join([f"{code}{codes.count(code)}" for code in sorted(set(codes))])


def dump_db_to_json():
    with open("data/zinc.json", "w") as f:
        sysout, sys.stdout = sys.stdout, f
        call_command("dumpdata",  "--exclude=contenttypes", verbosity=0)
    sys.stdout = sysout
