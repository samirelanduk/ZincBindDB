#! /usr/bin/env python3

"""When run, this script will build the ZincBind database from scratch."""

import sys
import os
sys.path.append(os.path.join("..", "zincbind"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
import django; django.setup()
from django.db import transaction
from core.utilities import *
from core.models import Pdb, Metal, Chain, ZincSite, Residue, CoordinateBond, ChainSiteInteraction
import atomium
from tqdm import tqdm

def main(json=True):
    # Get all PDBs which contain zinc
    codes = get_zinc_pdb_codes()
    print(f"There are {len(codes)} PDBs with zinc")

    # Which ones should be processed?
    codes = remove_checked_codes(codes)
    print(f"{len(codes)} are going to be checked")

    # Process each code
    for code in tqdm(codes):
        with transaction.atomic():

            # Get PDB
            pdb = atomium.fetch(code)

            # Get model
            model, assembly_id = get_best_model(pdb)

            # Save PDB record
            pdb_record = Pdb.create_from_atomium(pdb, assembly_id)

            # Check model is usable
            if model_is_skeleton(model):
                for zinc in model.atoms(element="ZN"):
                    Metal.create_from_atomium(zinc, pdb_record,
                     omission="No side chain information in PDB."
                    )
                continue

            # Save any zincs not in model
            for zinc in zincs_outside_model(model, pdb):
                Metal.create_from_atomium(zinc, pdb_record,
                 omission="Zinc in asymmetric unit but not biological assembly."
                )

            # Get metals
            metals = remove_duplicate_atoms(model.atoms(is_metal=True))

            # Determine liganding atoms of all metals
            metals = {m: get_atom_liganding_atoms(m) for m in metals}

            # Get binding site dicts
            sites = [{"metals": {m: v}, "count": 1} for m, v in metals.items()]
            merge_metal_groups(sites)

            # Aggregate duplicate sites
            aggregate_sites(sites)
            sites.sort(key=lambda s: min(a.id for a in s["metals"].keys()))

            # Remove sites with no zinc
            sites = [site for site in sites if "ZN" in [
             a.element for a in site["metals"].keys()
            ]]

            # Remove sites with not enough residues
            bad_sites = [s for s in sites if residue_count(s) < 2]
            for site in bad_sites:
                for metal in site["metals"]:
                    Metal.create_from_atomium(metal, pdb_record,
                     omission="Zinc has too few binding residues."
                    )
                sites.remove(site)

            # Remove sites with not enough liganding atoms
            bad_sites = [s for s in sites if liganding_atom_count(s) < 3]
            for site in bad_sites:
                for metal in site["metals"]:
                    Metal.create_from_atomium(metal, pdb_record,
                     omission="Zinc has too few liganding atoms."
                    )
                sites.remove(site)

            # Create chain records
            all_residues = residues_from_sites(sites)
            chains = get_chains_from_residues(all_residues)
            chain_dict = {}
            for chain in chains:
                sequence = get_chain_sequence(chain, all_residues)
                chain_dict[chain.id] = Chain.create_from_atomium(chain, pdb_record, sequence=sequence)

            # Save sites
            for index, site in enumerate(sites, start=1):
                # Create site record itself
                residues = get_site_residues(site)
                site_record = ZincSite.objects.create(
                 id=f"{pdb_record.id}-{index}", copies=site["count"],
                 family=create_site_code(residues), pdb=pdb_record,
                 residue_names="".join(set([f".{r.name}." for r in residues]))
                )

                # Create metals
                metals = {}
                for metal in site["metals"].keys():
                    metals[metal.id] = Metal.create_from_atomium(
                     metal, pdb_record, site=site_record
                    )

                # Create chain interaction
                chains = get_chains_from_residues(residues)
                for chain in chains:
                    sequence = get_chain_sequence(chain, residues)
                    ChainSiteInteraction.objects.create(
                     chain=chain_dict[chain.id], site=site_record,
                     sequence=sequence, spacers=get_spacers(sequence)
                    )

                # Create residue records
                atom_dict = {}
                for r in get_site_residues(site):
                    chain = chain_dict.get(r.chain.id) if isinstance(r, atomium.Residue) else None
                    Residue.create_from_atomium(r, chain, site_record, atom_dict)

                # Create bond records
                for metal, atoms in site["metals"].items():
                    for atom in atoms:
                        CoordinateBond.objects.create(
                         metal=metals[metal.id], atom=atom_dict[atom.id]
                        )

    # JSON?
    if json:
        print("Saving JSON...")
        dump_db_to_json()


if __name__ == "__main__": main()
