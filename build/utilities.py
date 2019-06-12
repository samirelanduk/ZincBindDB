import math
import requests
import atomium
from sites import remove_duplicate_atoms, get_atom_liganding_atoms
from sites import remove_salt_metals, merge_metal_groups, get_site_residues
from sites import get_site_chains
from chains import get_all_chains, get_all_residues, get_chain_sequence

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
    from factories import create_chain_record, create_site_record

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

    # Get list of binding site dicts from the metals dict
    sites = [{"metals": {m: v}} for m, v in metals.items()]

    # Merge those that share residues
    merge_metal_groups(sites)

    # Remove sites with no zinc
    sites = [site for site in sites if "ZN" in [
     a.element for a in site["metals"].keys()
    ]]

    # Sort sites to make ID allocation deterministic
    sites.sort(key=lambda s: min(a.id for a in s["metals"].keys()))

    # Add residues and chains to site dicts
    for site in sites:
        site["residues"] = get_site_residues(site)
        site["chains"] = get_site_chains(site)
    
    # Create chains involved in all binding sites
    chains, residues = get_all_chains(sites), get_all_residues(sites)
    chains_dict = {}
    for chain in chains:
        sequence = get_chain_sequence(chain, residues)
        chains_dict[chain.id] = create_chain_record(chain, pdb_record, sequence)
    
    # Save sites to database
    for index, site in enumerate(sites, start=1):
        site_record = create_site_record(site, pdb_record, index, chains_dict)



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


def create_site_family(residues):
    codes = [atomium.data.CODES.get(r.name, "X")
     for r in residues if isinstance(r, atomium.Residue)]
    return "".join([f"{c}{codes.count(c)}" for c in sorted(set(codes))])