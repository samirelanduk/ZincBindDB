#! /usr/bin/env python3

"""When run, this script will build the ZincBind database from scratch."""

import sys
import os
sys.path.append(os.path.join("..", "zincbind"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
import django; django.setup()
from django.db import transaction
from core.utilities import *
from core.models import Pdb, Metal, Chain, ZincSite, Residue, CoordinateBond
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

            # Get metal clusters from model
            clusters = cluster_zincs_with_residues(model.atoms(is_metal=True))

            # Remove unsuitable clusters
            rejected_clusters = []
            for cluster in clusters:
                # Does the cluster have enough residues?
                if residue_count(cluster) < 2:
                    for metal in cluster["metals"]:
                        Metal.create_from_atomium(metal, pdb_record,
                         omission="Zinc has too few binding residues."
                        )
                    rejected_clusters.append(cluster)
                    continue

                # Does the cluster have enough liganding atoms?
                if liganding_atom_count(cluster) < 3:
                    for metal in cluster["metals"]:
                        Metal.create_from_atomium(metal, pdb_record,
                         omission="Zinc has too few liganding atoms."
                        )
                    rejected_clusters.append(cluster)
                    continue
            for cluster in rejected_clusters: clusters.remove(cluster)

            # Create binding site from each cluster
            for index, cluster in enumerate(clusters, start=1):
                # Create site record itself
                site = ZincSite.objects.create(
                 id=f"{pdb_record.id}-{index}", copies=cluster["count"],
                 family=create_site_code(get_cluster_residues(cluster)), pdb=pdb_record
                )

                # Create metals
                metals = {}
                for metal in cluster["metals"].keys():
                    metals[metal.id] = Metal.create_from_atomium(metal, pdb_record, site=site)

                # Create chains
                all_residues = residues_from_clusters(clusters)
                residues = get_cluster_residues(cluster)
                chains = get_chains_from_residues(residues)
                chain_dict = {}
                for chain in chains:
                    chain_dict[chain.id] = Chain.create_from_atomium(chain, site, sequence=get_chain_sequence(chain, all_residues), site_sequence=get_chain_sequence(chain, residues))


                # Create residue records
                atom_dict = {}
                for r in get_cluster_residues(cluster):
                    chain = chain_dict.get(r.chain.id)
                    Residue.create_from_atomium(r, chain, site, atom_dict)

                # Create bond records
                for metal, atoms in cluster["metals"].items():
                    for atom in atoms:
                        CoordinateBond.objects.create(
                         metal=metals[metal.id], atom=atom_dict[atom.id]
                        )

    # JSON?
    if json:
        print("Saving JSON...")
        dump_db_to_json()


if __name__ == "__main__": main()
