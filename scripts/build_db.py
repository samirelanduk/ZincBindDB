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
    codes = get_zinc_pdb_codes()
    print(f"There are {len(codes)} PDBs with zinc")
    if not reset:
        checked = [p.id for p in Pdb.objects.all()]
        print(f"{len(checked)} have already beed checked")
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
            metals = pdb.model.atoms(metal=True) - pdb.model.atoms(metal=False)
            zinc_clusters = cluster_zincs_with_residues(metals)

            # Create chains
            chains = {}
            for chain in pdb.model.chains():
                chains[chain.id] = Chain.create_from_atomium(chain, pdb_record)

            # Create binding sites
            for cluster in zinc_clusters:
                # Create site record itself
                zinc_ids = "-".join(str(zinc.id) for zinc in cluster["metals"])
                site = ZincSite.objects.create(
                 id=f"{pdb_record.id}{zinc_ids}", pdb=pdb_record
                )

                # Create zinc records and their residues
                for metal in cluster["metals"]:
                    chain = chains[metal.molecule.id[0]]
                    Metal.create_from_atomium(metal, pdb_record, site, chain)

                # Create residue records
                for r in cluster["residues"]:
                    chain = chains[r.id[0]]
                    Residue.create_from_atomium(
                     r, chain, site
                    )

            # Delete uneeded chains



if __name__ == "__main__":
    main(reset="reset" in sys.argv)
