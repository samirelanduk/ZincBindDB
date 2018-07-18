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



def main(reset=False):
    # Get all PDBs which contain zinc
    codes = get_zinc_pdb_codes()[:20]
    print(f"There are {len(codes)} PDBs with zinc")
    if not reset:
        checked = [p.id for p in Pdb.objects.all()]
        print(f"{len(checked)} have already been checked")
        codes = [code for code in codes if code not in checked]


    # Go through each PDB
    for code in tqdm(codes):
    #for code in codes:
        with transaction.atomic():
            # Create the PDB record
            pdb = atomium.fetch(code, pdbe=True)
            if not pdb: continue
            pdb_record = Pdb.create_from_atomium(pdb)

            # Get zincs and cluster
            model = pdb.generate_best_assembly()
            metals = model.atoms(is_metal=True)
            while not metals:
                pdb.biomolecules.remove(pdb.best_assembly)
                model = pdb.generate_best_assembly()
                metals = model.atoms(is_metal=True)
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
                # Create site record itself
                site = ZincSite.objects.create(
                 id=f"{pdb_record.id}-{index}", pdb=pdb_record,
                )

                # Create residue records
                for r in cluster["residues"]:
                    chain = chains[r.chain.id]
                    Residue.create_from_atomium(
                     r, chain, site
                    )

                # Create zinc records and their residues
                for metal in cluster["metals"]:
                    chain = chains[metal.chain.id]
                    Metal.create_from_atomium(metal, site, chain)


if __name__ == "__main__":
    main(reset="reset" in sys.argv)
