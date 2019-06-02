#! /usr/bin/env python3

from utilities import *
setup_django()
from tqdm import tqdm
from django.db import transaction
from core.models import Pdb

def main():
    # What PDBs have zinc in them?
    codes = get_zinc_pdb_codes()
    print(f"There are {len(codes)} PDB codes with zinc")

    # How many should be checked
    current_codes = Pdb.objects.all().values_list("id", flat=True)
    codes_to_check = [code for code in codes if code not in current_codes]
    print(f"{len(codes_to_check)} of these need to be checked")

    # Check
    for code in tqdm(codes_to_check):
        with transaction.atomic():
            process_pdb_code(code)



if __name__ == "__main__":
    print()
    main()
    print()
