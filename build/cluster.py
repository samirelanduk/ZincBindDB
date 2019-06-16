#! /usr/bin/env python3

import sys
import os
from utilities import *
from chains import get_all_chains_fasta, get_chain_clusters
from sites import get_site_clusters, add_fingerprint_to_site
setup_django()
from tqdm import tqdm
from django.db import transaction
from django.db.models import F
from core.models import ChainCluster, Group, ZincSite, Chain

SEQUENCE_IDENTITY = 0.9

def main():
    from factories import create_chain_cluster_record, create_group_record

    # Check if CD-HIT is installed
    if not is_cd_hit_installed():
        print("Cannot proceed as CD-HIT is not installed or not in PATH")
        sys.exit()

    try:
        # Remove any existing clusters and groups
        clusters, groups = ChainCluster.objects.all(), Group.objects.all()
        text = f"Deleted {clusters.count()} chain clusters and {groups.count()} site groups"
        clusters.delete()
        groups.delete()
        print(text)

        # Save temporary FASTA file
        fasta = get_all_chains_fasta()
        with open("chains.fasta", "w") as f: f.write(fasta)
        print("Saved current chains to chains.fasta ({:.2f} KB)".format(len(fasta) / 1024))

        # Run CD-HIT
        clusters = get_chain_clusters(SEQUENCE_IDENTITY)
        print(f"Clustered chains into {len(clusters)} clusters ({SEQUENCE_IDENTITY * 100}% sequence identity)")

        # Save clusters to database
        print("Saving these to the database...")
        chain_dates = {chain.id: chain.date for chain in
         Chain.objects.all().annotate(date=F("pdb__deposition_date"))}
        with transaction.atomic():
            for cluster in tqdm(clusters):
                create_chain_cluster_record(cluster, chain_dates)
        for chain in Chain.objects.filter(cluster=None):
            create_chain_cluster_record([chain.id], chain_dates)
        
        # Cluster sites based on chain clusters
        print("Clustering zinc sites based on associated chains...")
        sites = ZincSite.objects.all().annotate(date=F("pdb__deposition_date"))
        for site in tqdm(sites):
            add_fingerprint_to_site(site)
        site_clusters = get_site_clusters(sites)

        # Save zinc site clusters to database
        print("Saving these clusters to the database...")
        with transaction.atomic():
            for sites in tqdm(site_clusters.values()):
                create_group_record(sites)

    finally:
        # Remove any temporary files saved
        for filename in ["chains.fasta", "temp", "temp.clstr"]:
            try:
                os.remove(filename)
            except: pass



if __name__ == "__main__":
    print()
    main()
    print()