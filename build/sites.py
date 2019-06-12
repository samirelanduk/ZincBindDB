import math
from itertools import combinations
import atomium

def remove_duplicate_atoms(atoms):
    """Takes a set of atoms, and removes duplicates. For each element that is
    represented, it creates an empty set of unique atoms. It then goes through
    all the atoms from the original set of that element, and if the atom is
    within 1 Angstrom of any atoms in the unique set, it is discarded -
    otherwise it is added to the unique set. The final set is the union of all
    the different elements' unique sets."""

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


def get_atom_liganding_atoms(metal):
    """Takes an atom and gets all non-metal, non-carbon, non-hydrogen atoms
    within 3Å. It then goes through all these atoms, starting with the closest,
    and if any of them have a coordination bond angle with a closer atom of
    less than 45 degrees, it is discarded."""

    kwargs = {"cutoff": 3, "is_metal": False}
    nearby_atoms = [a for a in metal.nearby_atoms(**kwargs) if a.element not in "CH"]
    nearby_atoms = remove_duplicate_atoms(nearby_atoms)
    nearby_atoms = sorted(nearby_atoms, key=lambda a: a.distance_to(metal))
    liganding = []
    for atom in nearby_atoms:
        for ligand in liganding:
            if metal.angle(atom, ligand) < math.pi / 4:
                break
        else:
            liganding.append(atom)
    return liganding


def remove_salt_metals(metals):
    """Takes a dictionary of metal: atoms mapping, goes through each metal and
    removes those which don't have at least three liganding atoms from residues.
    Atoms from ligands don't count.

    The useless metals, presumed to be salts, are returned as a list."""

    useless_metals = []
    for metal, atoms in metals.items():
        if len([a for a in atoms if isinstance(a.het, atomium.Residue)]) < 3:
            useless_metals.append(metal)
    for metal in useless_metals: del metals[metal]
    return useless_metals


def merge_metal_groups(sites):
    """Takes a dictionary in which the keys are metal atoms and the values are
    the set of residues that bind to them.
    It then creates a list of sites from this, where each site is a dict
    object with metals and residues. Two metals and their residues will be
    merged together if they share residues."""

    while not check_sites_have_unique_residues(sites):
        for site1, site2 in combinations(sites, 2):
            if get_site_residues(site1).intersection(get_site_residues(site2)):
                site1["metals"].update(site2["metals"])
                sites.remove(site2)
                break
    return sites


def check_sites_have_unique_residues(sites):
    residues = set()
    all_residues = []
    for site in sites:
        site_residues = get_site_residues(site)
        for res in site_residues:
            residues.add(res)
            all_residues.append(res)
    return len(residues) == len(all_residues)


def get_site_residues(site):
    site_residues = set()
    for atoms in site["metals"].values():
        for atom in atoms:
            site_residues.add(atom.het)
    return site_residues


def get_site_chains(site):
    site_chains = set()
    for res in site["residues"]:
        if isinstance(res, atomium.Residue):
            if res.chain.id not in [c.id for c in site_chains]:
                site_chains.add(res.chain)
    return site_chains