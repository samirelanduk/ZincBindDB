#! /usr/bin/env python3

def setup_django():
    import os, django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    django.setup()


setup_django()
import math
import requests
import atomium
from tqdm import tqdm
from django.db import transaction
from core.models import Pdb


def get_zinc_pdb_codes():
    """Gets PDB codes for all structures with a zinc atom in them.
    If the response returned has an error code of 500, or if there are fewer
    than 10,000 PDB codes sent back, an error will be thrown."""

    query = "<orgPdbQuery>"\
    "<queryType>org.pdb.query.simple.ChemCompFormulaQuery</queryType>"\
    "<formula>ZN</formula></orgPdbQuery>"
    url = "https://www.rcsb.org//pdb/rest/search/"
    response = requests.post(url, data=query.encode(), headers={
     "Content-Type": "application/x-www-form-urlencoded"
    })
    if response.status_code == 200:
        codes = response.text.split()
        if len(codes) > 10000:
            return response.text.split()
    raise Exception("RCSB didn't send back PDB codes")


def process_pdb_code(code):
    # Get PDB
    pdb = atomium.fetch(code)
    model, assembly_id = get_best_model(pdb)
    create_pdb_record(pdb, assembly_id)


def get_best_model(pdb):
    assemblies = sorted(pdb.assemblies, key=lambda a: math.inf
     if a["delta_energy"] is None else a["delta_energy"])
    if assemblies:
        model = pdb.generate_assembly(assemblies[0]["id"])
        metals = model.atoms(is_metal=True)
        while not metals:
            assemblies.pop(0)
            model = pdb.generate_assembly(assemblies[0]["id"])
            metals = model.atoms(is_metal=True)
        return model, assemblies[0]["id"]
    else:
        return pdb.model, None


def create_pdb_record(pdb, assembly_id):
    return Pdb.objects.create(
     id=pdb.code, rvalue=pdb.rvalue, classification=pdb.classification,
     deposition_date=pdb.deposition_date, organism=pdb.source_organism,
     expression_system=pdb.expression_system, technique=pdb.technique,
     keywords=", ".join(pdb.keywords) if pdb.keywords else "", title=pdb.title,
     resolution=pdb.resolution, skeleton=model_is_skeleton(pdb.model),
     assembly=assembly_id
    )


def model_is_skeleton(model):
    for residue in model.residues():
        atom_names = set([atom.name for atom in residue.atoms()])
        for name in atom_names:
            if name not in ["C", "N", "CA", "O"]:
                return False
    return True


def main():
    # What PDBs have zinc in them?
    codes = get_zinc_pdb_codes()
    print(f"There are {len(codes)} PDB codes with zinc")

    # How many should be checked
    current_codes = Pdb.objects.all().values_list("id", flat=True)
    codes_to_check = [code for code in codes if code not in current_codes]
    print(f"{len(codes_to_check)} of these need to be checked")

    # Check
    for code in tqdm(codes_to_check[:10]):
        with transaction.atomic():
            process_pdb_code(code)




print()
main()
print()
