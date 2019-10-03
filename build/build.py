#! /usr/bin/env python3

"""This script will update the database with new PDBs, but won't cluster."""

from utilities import *
setup_django()
from tqdm import tqdm
from django.db import transaction
from core.models import Pdb

def process_pdb_code(code):
    """Builds all the relevant objects for any given PDB code."""

    from factories import create_pdb_record, create_metal_record
    from factories import create_chain_record, create_site_record

    # Get PDB
    log(f"Fetching {code}")
    pdb = atomium.fetch(code)
    log(f"Getting best {code} assembly")
    model, assembly_id = get_best_model(pdb)
    model.optimise_distances()
    log(f"Saving {code} to database")
    pdb_record = create_pdb_record(pdb, assembly_id)

    # Check model is usable
    if model_is_skeleton(model):
        for zinc in sorted(model.atoms(element="ZN"), key=lambda m: m.id):
            create_metal_record(zinc, pdb_record,
             omission="No side chain information in PDB."
            )
        return

    # Save any zincs not in model
    for zinc in sorted(zincs_outside_model(model, pdb), key=lambda m: m.id):
        create_metal_record(zinc, pdb_record,
         omission="Zinc in asymmetric unit but not biological assembly."
        )

    # Get metals
    log(f"Finding {code} liganding atoms")
    metals = remove_duplicate_atoms(model.atoms(is_metal=True))

    # Determine liganding atoms of all metals
    metals = {m: get_atom_liganding_atoms(m) for m in metals}

    # Ignore metals with too few liganding atoms
    useless_metals = remove_salt_metals(metals)
    for metal in sorted(useless_metals, key=lambda m: m.id):
        if metal.element == "ZN":
            create_metal_record(metal, pdb_record,
             omission="Zinc has too few liganding atoms."
            )

    log(f"Processing {code} sites")
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
    log(f"Processing {code} chains")
    chains, residues = get_all_chains(sites), get_all_residues(sites)
    chains_dict = {}
    for chain in chains:
        sequence = get_chain_sequence(chain, residues)
        chains_dict[chain.id] = create_chain_record(chain, pdb_record, sequence)
    
    # Save sites to database
    for index, site in enumerate(sites, start=1):
        log(f"Saving {code} site")
        site_record = create_site_record(site, pdb_record, index, chains_dict)


def main():
    log("\n\n\nSTARTING DATABASE BUILD")
    # What PDBs have zinc in them?
    codes = get_zinc_pdb_codes()
    print(f"There are {len(codes)} PDB codes with zinc")

    # How many should be checked
    current_codes = Pdb.objects.all().values_list("id", flat=True)
    codes_to_check = [code for code in codes if code not in current_codes]
    print(f"{len(codes_to_check)} of these need to be checked")

    # Check
    for code in tqdm(codes_to_check):
        with transaction.atomic():
            process_pdb_code(code)



if __name__ == "__main__":
    print()
    main()
    print()
