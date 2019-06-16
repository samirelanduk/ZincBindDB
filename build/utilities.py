"""Contains utility functions that don't belong anywhere else."""

import math
import requests
import subprocess
from datetime import datetime
import atomium
from sites import remove_duplicate_atoms, get_atom_liganding_atoms
from sites import remove_salt_metals, merge_metal_groups, get_site_residues
from sites import get_site_chains
from chains import get_all_chains, get_all_residues, get_chain_sequence

def setup_django():
    """Sets up the django environment so that it can be used in a script."""

    import os, sys, django
    sys.path.append(os.path.join("..", "zincbinddb"))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    django.setup()


def log(text):
    """Writes a line to the log file."""
    
    with open("data/build.log", "a") as f:
        f.write("{}: {}\n".format(
         datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), text
        ))


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


def get_best_model(pdb):
    """Works out which assembly in a PDB has the lowest energy and returns that
    model."""

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


def model_is_skeleton(model):
    """Checks to see if a model contains of nothing but alpha carbons."""

    for residue in model.residues():
        atom_names = set([atom.name for atom in residue.atoms()])
        for name in atom_names:
            if name not in ["C", "N", "CA", "O"]:
                return False
    return True


def zincs_outside_model(model, pdb):
    """Gets all zinc atoms that are not in some assembly but are in the raw PDB
    model."""

    au_zincs = pdb.model.atoms(element="ZN")
    assembly_zinc_ids = [atom.id for atom in model.atoms(element="ZN")]
    return [z for z in au_zincs if z.id not in assembly_zinc_ids]


def is_cd_hit_installed():
    """Checks if the CD-hit binary is installed."""

    p = subprocess.Popen(
     "which cd-hit", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    out, err = p.communicate()
    return bool(out)