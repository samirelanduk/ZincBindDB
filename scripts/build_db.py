#! /usr/bin/env python3

"""When run, this script will build the ZincBind database from scratch."""

import sys
import os
sys.path.append(os.path.join("..", "zincbind"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
import django; django.setup()
from django.db import transaction
from zinc.utilities import *
from zinc.models import Pdb, Chain, ZincSite, Metal, Residue
import atomium
from tqdm import tqdm

def main():
    # Get all PDBs which contain zinc
    codes = get_zinc_pdb_codes()
    print(f"There are {len(codes)} PDBs with zinc")

    # Go through each PDB
    for code in tqdm(codes):
    #for code in codes:
        with transaction.atomic():
            # Create the PDB record
            pdb = atomium.fetch(code, pdbe=True)
            if not pdb: continue
            pdb_record = Pdb.create_from_atomium(pdb)

            # Get zincs and cluster
            metals = pdb.model.atoms(metal=True) - pdb.model.atoms(metal=False)
            zinc_clusters = cluster_zincs_with_residues(metals)

            # Create chains
            chains = {}
            for chain in get_chains_from_clusters(zinc_clusters):
                chains[chain.id] = Chain.create_from_atomium(chain, pdb_record)

            # Create binding sites
            for cluster in zinc_clusters:
                # Create site record itself
                zinc_ids = "-".join(str(zinc.id) for zinc in cluster["metals"])
                site = ZincSite.objects.create(
                 id=f"{pdb_record.id}{zinc_ids}", pdb=pdb_record
                )

                # Create zinc records
                for metal in cluster["metals"]:
                    Metal.create_from_atomium(metal, site)

                # Create residue records
                for r in cluster["residues"]:
                    chain = None
                    if r.__class__.__name__ == "Residue":
                        chain = chains[r.chain.id]
                    Residue.create_from_atomium(
                     r, site, chain, r.chain.residues().index(r) if chain else 0
                    )


if __name__ == "__main__":
    main()
