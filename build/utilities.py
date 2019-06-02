import math
from itertools import combinations
import requests
import atomium

def setup_django():
    import os, sys, django
    sys.path.append(os.path.join("..", "zincbinddb"))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    django.setup()


def get_zinc_pdb_codes():
    """Gets PDB codes for all structures with a zinc atom in them.
    If the response returned has an error code of 500, or if there are fewer
    than 10,000 PDB codes sent back, an error will be thrown."""

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


def process_pdb_code(code):
    from factories import create_pdb_record, create_metal_record

    # Get PDB
    pdb = atomium.fetch(code)
    model, assembly_id = get_best_model(pdb)
    pdb_record = create_pdb_record(pdb, assembly_id)

    # Check model is usable
    if model_is_skeleton(model):
        for zinc in model.atoms(element="ZN"):
            create_metal_record(zinc, pdb_record,
             omission="No side chain information in PDB."
            )
        return

    # Save any zincs not in model
    for zinc in zincs_outside_model(model, pdb):
        create_metal_record(zinc, pdb_record,
         omission="Zinc in asymmetric unit but not biological assembly."
        )

    # Get metals
    metals = remove_duplicate_atoms(model.atoms(is_metal=True))

    # Determine liganding atoms of all metals
    metals = {m: get_atom_liganding_atoms(m) for m in metals}

    # Ignore metals with too few liganding atoms
    useless_metals = remove_salt_metals(metals)
    for metal in useless_metals:
        if metal.element == "ZN":
            create_metal_record(metal, pdb_record,
             omission="Zinc has too few liganding atoms."
            )

    # Get binding site dicts
    sites = [{"metals": {m: v}, "count": 1} for m, v in metals.items()]
    merge_metal_groups(sites)

    # Remove sites with no zinc
    sites = [site for site in sites if "ZN" in [
     a.element for a in site["metals"].keys()
    ]]



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
    useless_metals = []
    for metal, atoms in metals.items():
        if len([a for a in atoms if isinstance(a.structure, atomium.Residue)]) < 3:
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
            site_residues.add(atom.structure)
    return site_residues
