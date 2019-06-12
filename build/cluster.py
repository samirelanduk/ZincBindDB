#! /usr/bin/env python3

import sys
import os
from utilities import *
from chains import get_all_chains_fasta
setup_django()
from tqdm import tqdm
from django.db import transaction
from core.models import ChainCluster, Group

def main():
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

    finally:
        # Remove any temporary files saved
        for filename in ["chains.fasta"]:
            try:
                os.remove(filename)
            except: pass



if __name__ == "__main__":
    print()
    main()
    print()