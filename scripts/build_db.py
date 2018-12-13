#! /usr/bin/env python3

"""When run, this script will build the ZincBind database from scratch."""

import sys
import os
sys.path.append(os.path.join("..", "zincbind"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
import django; django.setup()
from django.db import transaction
from django.core.management import call_command
from core.utilities import *
from core.models import Pdb, Metal, Chain, ZincSite, Residue
import atomium
from tqdm import tqdm
from multiprocessing import Pool


def process_code(code):
    with transaction.atomic():
        # Get PDB
        try:
            pdb = atomium.fetch(code)
        except ValueError:
            return

        # Which assembly should be used?
        model = pdb.generate_best_assembly()
        metals = model.atoms(is_metal=True)
        while not metals:
            pdb.assemblies.remove(pdb.best_assembly)
            model = pdb.generate_best_assembly()
            metals = model.atoms(is_metal=True)

        # Save the PDB
        pdb_record = Pdb.create_from_atomium(pdb)

        # Is the PDB usable?
        if model_is_skeleton(model):
            zincs = model.atoms(element="ZN")
            for zinc in zincs:
                Metal.create_from_atomium(
                 zinc, pdb_record,
                 omission="No residue side chain information in PDB."
                )
            return

        # Are any PDB zincs not in assembly
        au_zincs = pdb.model.atoms(element="ZN")
        assembly_zinc_ids = [atom.id for atom in model.atoms(element="ZN")]
        for zinc in au_zincs:
            if zinc.id not in assembly_zinc_ids:
                Metal.create_from_atomium(
                 zinc, pdb_record,
                 omission="Zinc was in asymmetric unit but not biological assembly."
                )

        # Get zinc clusters
        zinc_clusters = cluster_zincs_with_residues(metals)

        # Create chains
        chains = {}
        for cluster in zinc_clusters:
            for o in cluster["residues"].union(cluster["metals"]):
                chains[o.chain.id] = o.chain
        for chain_id, chain in chains.items():
            chains[chain_id] = Chain.create_from_atomium(chain, pdb_record)

        # Create binding sites
        for index, cluster in enumerate(zinc_clusters, start=1):
            # Does the cluster even have any residues?
            if len([r for r in cluster["residues"] if r.__class__.__name__ == "Residue"]) < 2:
                for metal in cluster["metals"]:
                    Metal.create_from_atomium(
                     metal, pdb_record,
                     omission="Zinc has too few binding residues."
                    )
                continue
            # Does the cluster have enough liganding atoms?
            atoms = []
            for residue in cluster["residues"]:
                atoms += [a for a in residue.atoms() if a.liganding]
            if len(atoms) < 3:
                for metal in cluster["metals"]:
                    Metal.create_from_atomium(
                     metal, pdb_record, omission="Zinc has too few liganding atoms."
                    )
                continue

            # Create site record itself
            site = ZincSite.objects.create(
             id=f"{pdb_record.id}-{index}", pdb=pdb_record,
             code=create_site_code(cluster["residues"]),
             copies=cluster["count"]
            )

            # Create metals
            for metal in cluster["metals"]:
                Metal.create_from_atomium(metal, pdb_record, site=site)

            # Create residue records
            for r in cluster["residues"]:
                chain = chains[r.chain.id]
                Residue.create_from_atomium(r, chain, site)


def main(reset=False, json=True, multiprocess=True):
    # Get all PDBs which contain zinc
    codes = get_zinc_pdb_codes()
    print(f"There are {len(codes)} PDBs with zinc")
    if not reset:
        checked = [p.id for p in Pdb.objects.all()]
        print(f"{len(checked)} have already been checked")
        codes = [code for code in codes if code not in checked]

    # Go through each PDB
    if multiprocess:
        for code in tqdm(codes):
            process_code(code)
    else:
        for code in codes: process_code(code)

    # JSON?
    if json:
        print("Saving JSON")
        sysout = sys.stdout
        with open("data/zinc.json", "w") as f:
            sys.stdout = f
            call_command(
             "dumpdata",  "--exclude=contenttypes", verbosity=0
            )
            sys.stdout = sysout


if __name__ == "__main__":
    main(reset="reset" in sys.argv)
