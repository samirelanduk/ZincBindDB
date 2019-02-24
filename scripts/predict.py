#! /usr/bin/env python3

"""When run, this script will look for binding sites in some file."""

import sys
import os
from pathlib import Path
sys.path.append(os.path.join("..", "zincbind"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
import django; django.setup()
from django.db import transaction

# Where is the file?
try:
    file_path = sys.argv[1]
except:
    print("\nWhere is the file?\n")
    sys.exit()

# What is the folder?
folder = os.path.dirname(file_path) or os.getcwd()

# Start log
with open(f"{folder}/output.txt", "w") as f:
    f.write("Starting job...\n\n")

from time import sleep
sleep(10)

# Update log
with open(f"{folder}/output.txt", "a") as f:
    f.write("More...\n\n")
