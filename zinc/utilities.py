import requests
from itertools import combinations
from atomium.structures import Chain, Residue

class RcsbError(Exception):
    """Error raised if there's a problem talking to the RCSB web services."""
    pass



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

    for chain in model.chains():
        atom_names = set([atom.name for atom in chain.atoms()])
        for name in atom_names:
            if name not in ["C", "N", "CA", "O"]:
                return False
    return True


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


def check_clusters_have_unique_residues(clusters):
    """Takes a list of clusters and returns True if they don't share any
    residues in common."""

    residue_count = sum([len(cluster["residues"]) for cluster in clusters])
    unique_residue_count = len(set.union(
     *[cluster["residues"] for cluster in clusters]
    ))
    return residue_count == unique_residue_count


def merge_metal_groups(metals):
    """Takes a dictionary in which the keys are metal atoms and the values are
    the set of residues that bind to them.

    It then creates a list of clusters from this, where each cluster is a dict
    object with metals and residues. Two metals and their residues will be
    merged together if they share residues."""

    clusters = [{"metals": {metal}, "residues": residues}
     for metal, residues in metals.items()]
    while not check_clusters_have_unique_residues(clusters):
        for cluster1, cluster2 in combinations(clusters, 2):
            if cluster1["residues"].intersection(cluster2["residues"]):
                cluster1["metals"].update(cluster2["metals"])
                cluster1["residues"].update(cluster2["residues"])
                clusters.remove(cluster2)
                break
    return clusters


def cluster_zincs_with_residues(metals):
    """Takes a set of metal atoms and creates clusters of them, with metals
    grouped together if they share binding residues. It will only return those
    which have at least one zinc atom in the metals."""

    metals = {metal: [] for metal in metals}
    for metal in metals:
        metals[metal] = get_atom_binding_residues(metal)
    clusters = merge_metal_groups(metals)
    return [c for c in clusters if "ZN" in [a.element for a in c["metals"]]]
