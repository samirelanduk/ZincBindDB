#! /usr/bin/env python3

import sys
from utilities import *
setup_django()
from tqdm import tqdm
from django.db import transaction
from core.models import ChainCluster, Group

# Check if CD-HIT is installed
if not is_cd_hit_installed():
    print("Cannot proceed as CD-HIT is not installed or not in PATH")
    sys.exit()

# Remove any existing clusters and groups
print("Removing previous clusters and groups from database...")
ChainCluster.objects.all().delete()
Group.objects.all().delete()