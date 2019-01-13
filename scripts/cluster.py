#! /usr/bin/env python3

"""Takes a database created by build_db.py and clusters chains and zincsites."""

import sys
import os
sys.path.append(os.path.join("..", "zincbind"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
import django; django.setup()
from django.db import transaction
from django.db.models import F
import subprocess
import re
from core.models import *
from core.utilities import get_group_information
from tqdm import tqdm
print("")

SEQUENCE_IDENTITY = 0.9

# Check if CD-HIT is installed
p = subprocess.Popen("which cd-hit", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
out, err = p.communicate()
if not out:
    print("Cannot proceed as CD-HIT is not installed or not in PATH\n")
    sys.exit()


try:
    print("Removing previous clusters from database...")
    ChainCluster.objects.all().delete()
    Group.objects.all().delete()

    print("Creating FASTA file with {} chains...".format(Chain.objects.count()))
    lines = []
    for chain in Chain.objects.all():
        lines.append(">lcl|" + str(chain.id))
        sequence = chain.sequence
        while sequence:
            lines.append(sequence[:80])
            sequence = sequence[80:]
    with open("data/chains.fasta", "w") as f:
        f.write("\n".join(lines))
    size = sum([len(line) for line in lines]) / 1024
    print("Saved to chains.fasta ({:.2f} KB)".format(size))

    print("Running job...")
    subprocess.call(
     "cd-hit -i data/chains.fasta -d 0 -o temp -c {} -n 5 -G 1 -g 1 -b 20 -s 0.0 -aL "
     "0.0 -aS 0.0 -T 4 -M 32000".format(SEQUENCE_IDENTITY),
     shell=True, stdout=subprocess.PIPE
    )

    with open("temp.clstr") as f:
        data = f.read()
    clusters = data.split(">Cluster ")[1:]
    clusters = [re.compile(r">(.+?)\.\.\.").findall(c) for c in clusters]
    clusters = [[chain.split("|")[1] for chain in cluster] for cluster in clusters]
    print("There are {} clusters".format(len(clusters)))

    print("Writing Chain clusters to database...")
    with transaction.atomic():
        for cluster in tqdm(clusters):
            cluster_object = ChainCluster.objects.create()
            for chain_id in cluster:
                chain = Chain.objects.get(id=chain_id)
                chain.cluster = cluster_object
                chain.save()

    print("Assigning Zinc Sites to clusters...")
    sites = ZincSite.objects.all().annotate(
     resolution=F("pdb__resolution")
    )
    for site in tqdm(sites):
        chain_clusters = set([
         str(res.chain.cluster.id) for res in site.residue_set.all() if res.chain and res.chain.cluster
        ])
        site.fingerprint = "_".join(sorted(chain_clusters)) + "__" + "_".join(
         [str(res.chain_signature) for res in site.residue_set.exclude(chain_signature="")]
        )

    unique_sites = {}
    for site in sites:
        if site.fingerprint not in unique_sites:
            unique_sites[site.fingerprint] = []
        unique_sites[site.fingerprint].append(site)

    print("Writing ZincSite clusters to database...")
    with transaction.atomic():
        for index, fingerprint in enumerate(tqdm(unique_sites)):
            keywords, classifications = get_group_information(unique_sites[fingerprint])
            group = Group.objects.create(
             family=unique_sites[fingerprint][0].family, keywords=keywords, classifications=classifications
            )
            for site in unique_sites[fingerprint]:
                site.group = group
                site.save()
            if unique_sites[fingerprint]:
                best_site = sorted(unique_sites[fingerprint],
                 key=lambda s: s.resolution if s.resolution else 100)[0]
                best_site.representative = True
                best_site.save()

    print("Building BLAST database...\n")
    subprocess.call(
     "makeblastdb -in data/chains.fasta -dbtype prot",
     shell=True, stdout=subprocess.PIPE
    )

finally:
    subprocess.call("rm temp*", shell=True)
