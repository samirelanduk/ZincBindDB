#! /usr/bin/env python3

import sys
import os
import subprocess
from utilities import setup_django
from chains import get_all_chains_fasta
setup_django()

fasta = get_all_chains_fasta()
with open("data/chains.fasta", "w") as f: f.write(fasta)
print("Saved current chains to chains.fasta ({:.2f} KB)".format(len(fasta) / 1024))

print("Building BLAST database...\n")
subprocess.call(
 "makeblastdb -in data/chains.fasta -dbtype prot",
 shell=True, stdout=subprocess.PIPE
)