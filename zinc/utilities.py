import requests
import logging
import time
import os
from datetime import datetime
from itertools import combinations
from atomium.structures import Chain, Residue

class RcsbError(Exception):
    """Error raised if there's a problem talking to the RCSB web services."""
    pass



def get_log():
    """Creates a logger object that writes to a file at data/logs."""

    logger = logging.getLogger("Build Script")
    logger.setLevel(logging.INFO)
    os.environ["TZ"] = "Europe/London"
    time.tzset()
    handler = logging.FileHandler(
     "data/logs/" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S.log")
    )
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


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
    raise RcsbError("RCSB didn't send back PDB codes")


def model_is_skeleton(model):
    """Returns ``True`` if the model given only contains backbone atoms."""

    for residue in model.residues():
        atom_names = set([atom.name for atom in residue.atoms()])
        for name in atom_names:
            if name not in ["C", "N", "CA", "O"]:
                return False
    return True


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

    metals = {metal: [] for metal in metals}
    for metal in metals:
        metals[metal] = get_atom_binding_residues(metal)
    clusters = merge_metal_groups(metals)
    for cluster in clusters: remove_duplicates_from_cluster(cluster)
    aggregate_clusters(clusters)
    return [c for c in clusters if "ZN" in [a.element for a in c["metals"]]]


def get_atom_binding_residues(metal):
    """Takes an atom and gets all residues within 3Å - including ligands.
    In the case of zinc atoms, it will only use nitrogen, oxygen or sulphur
    atoms. For other atoms it will take everything except carbons.

    It will also mark atoms as 'liganding' or otherwise."""

    kwargs = {
     "cutoff": 3, "is_metal": False,
     "element_regex": "[NOS]" if metal.element == "ZN" else "[^C]"
    }
    nearby_residues = metal.nearby_residues(ligands=True, **kwargs)
    for residue in nearby_residues:
        for atom in residue.atoms():
            atom.liganding = False
    for atom in metal.nearby_atoms(**kwargs): atom.liganding = True
    return nearby_residues


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
