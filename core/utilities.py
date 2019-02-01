import requests
import logging
import time
import os
import sys
import math
from datetime import datetime
from collections import Counter
from atomium.data import CODES
from itertools import combinations
from atomium.structures import Chain, Residue
from django.core.management import call_command
from core.models import Pdb
from pprint import pprint

CODES = CODES.copy()
CODES["HOH"] = "w"

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


def remove_checked_codes(codes):
    checked = [p.id for p in Pdb.objects.all()]
    return [c for c in codes if c not in checked]


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


def model_is_skeleton(model):
    """Returns ``True`` if the model given only contains backbone atoms."""

    for residue in model.residues():
        atom_names = set([atom.name for atom in residue.atoms()])
        for name in atom_names:
            if name not in ["C", "N", "CA", "O"]:
                return False
    return True


def zincs_outside_model(model, pdb):
    au_zincs = pdb.model.atoms(element="ZN")
    assembly_zinc_ids = [atom.id for atom in model.atoms(element="ZN")]
    return [z for z in au_zincs if z.id not in assembly_zinc_ids]


def site_zincs_with_residues(metals):
    """This function takes a set of atoms - all the metal atoms found in an
    atomium model.

    For each atom it will identify the binding residues for that atom and
    associate them with each other.

    From this dictionary, a list of site dictionaries will be made. In the
    simplest case, each metal will be a site, but two metal atoms will be
    merged into one site if they share binding residues.

    Then, duplicates will be removed. Two sites are duplicates if they have
    the same metal atom IDs - this is usually created from symmetry operations.

    Finally sites with no zinc in are removed."""

    metals = remove_duplicate_atoms(metals)
    metals = {metal: [] for metal in metals}
    for metal in metals:
        metals[metal] = get_atom_liganding_atoms(metal)
    sites = merge_metal_groups(metals)
    aggregate_sites(sites)
    return [c for c in sites if "ZN" in [a.element for a in c["metals"].keys()]]


def remove_duplicate_atoms(atoms):
    new_set = set()
    elements = set([m.element for m in atoms])
    for element in elements:
        relevant_atoms = [m for m in atoms if m.element == element]
        unique_relevant = set()
        for r in relevant_atoms:
            for u in unique_relevant:
                if r.distance_to(u) < 1:
                    break
            else:
                unique_relevant.add(r)
        new_set.update(unique_relevant)
    return new_set


def get_atom_liganding_atoms(metal):
    """Takes an atom and gets all residues within 3Å - including ligands.
    In the case of zinc atoms, it will only use nitrogen, oxygen or sulphur
    atoms. For other atoms it will take everything except carbons.

    It will also mark atoms as 'liganding' or otherwise."""

    kwargs = {"cutoff": 3, "is_metal": False}
    nearby_atoms = [a for a in metal.nearby_atoms(**kwargs) if a.element not in "CH"]
    nearby_atoms = remove_duplicate_atoms(nearby_atoms)
    nearby_atoms = sorted(nearby_atoms, key=lambda a: a.distance_to(metal))
    liganding = []
    for atom in nearby_atoms:
        for ligand in liganding:
            if metal.angle(atom, ligand) < math.pi / 4:
                break
        else:
            liganding.append(atom)
    return liganding


def remove_duplicate_residues(residues):
    molecules = [r for r in residues if len(r.atoms()) > 1]
    atoms = {r.atom(): r for r in residues if len(r.atoms()) == 1}
    unique_atoms = remove_duplicate_atoms(atoms.keys())
    for atom in unique_atoms:
        molecules.append(atoms[atom])
    return set(molecules)


def merge_metal_groups(sites):
    """Takes a dictionary in which the keys are metal atoms and the values are
    the set of residues that bind to them.

    It then creates a list of sites from this, where each site is a dict
    object with metals and residues. Two metals and their residues will be
    merged together if they share residues."""

    while not check_sites_have_unique_residues(sites):
        for site1, site2 in combinations(sites, 2):
            if get_site_residues(site1).intersection(get_site_residues(site2)):
                site1["metals"].update(site2["metals"])
                sites.remove(site2)
                break
    return sites


def check_sites_have_unique_residues(sites):
    residues = set()
    all_residues = []
    for site in sites:
        site_residues = get_site_residues(site)
        for res in site_residues:
            residues.add(res)
            all_residues.append(res)
    return len(residues) == len(all_residues)


def get_site_residues(site):
    site_residues = set()
    for atoms in site["metals"].values():
        for atom in atoms:
            site_residues.add(atom.structure)
    return site_residues


def aggregate_sites(sites):
    """Takes a list of site dictionaries and merges those with the same metal
    IDs."""

    while not check_sites_have_unique_sites(sites):
        for site1, site2 in combinations(sites, 2):
            if set([m.id for m in site1["metals"].keys()]) ==\
             set([m.id for m in site2["metals"].keys()]):
                site1["count"] += 1
                sites.remove(site2)
                break


def check_sites_have_unique_sites(sites):
    """Takes a list of sites and returns True if they have any equivalent
    sites."""

    site_ids = [frozenset([
     m.id for m in site["metals"].keys()
    ]) for site in sites]
    unique_ids = set(site_ids)
    return len(site_ids) == len(unique_ids)


def create_chains_dict(sites):
    chains = {}
    for site in sites:
        for o in get_site_residues(site):
            chains[o.chain.id] = o.chain
    return chains


def residue_count(site):
    return len([r for r in get_site_residues(site) if isinstance(r, Residue)])


def liganding_atom_count(site):
    liganding_atoms = []
    for atoms in site["metals"].values():
        for atom in atoms:
            if isinstance(atom.structure, Residue):
                liganding_atoms.append(atom)
    return len(liganding_atoms)


def create_site_code(residues):
    codes = [CODES.get(r.name, "X") for r in residues if r.__class__.__name__ == "Residue"]
    return "".join([f"{code}{codes.count(code)}" for code in sorted(set(codes))])


def residues_from_sites(sites):
    all_residues = []
    for c in sites:
        all_residues += get_site_residues(c)
    return all_residues


def get_chains_from_residues(residues):
    chains = set()
    for res in residues:
        if isinstance(res, Residue) and res.chain.id not in [c.id for c in chains]:
            chains.add(res.chain)
    return chains


def get_chain_sequence(chain, residues):
    full = "".join(res.code for res in chain)
    alignment = align_sequences(full, chain.sequence)
    seq, indices, dash_count = "", [], 0
    for i, char in enumerate(alignment[0]):
        if char == "-":
            dash_count += 1
        elif chain[i - dash_count].id in [r.id for r in residues]:
            indices.append(i)
    for i, char in enumerate(chain.sequence):
        seq += char.upper() if i in indices else char.lower()
    return seq


def match_score(alpha, beta, match_award, mismatch_penalty, gap_penalty):
    """Adapted from github.com/alevchuk/pairwise-alignment-in-python/"""

    if alpha == beta:
        return match_award
    elif alpha == '-' or beta == '-':
        return gap_penalty
    else:
        return mismatch_penalty


def align_sequences(seq1, seq2):
    """Adapted from github.com/alevchuk/pairwise-alignment-in-python/"""

    match_award      = 10
    mismatch_penalty = -5
    gap_penalty      = -5
    m, n = len(seq1), len(seq2)
    score = [[0 for y in range(n + 1)] for x in range(m + 1)]
    for i in range(0, m + 1): score[i][0] = gap_penalty * i
    for j in range(0, n + 1): score[0][j] = gap_penalty * j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            match = score[i - 1][j - 1] + match_score(
             seq1[i-1], seq2[j-1], match_award, mismatch_penalty, gap_penalty
            )
            delete = score[i - 1][j] + gap_penalty
            insert = score[i][j - 1] + gap_penalty
            score[i][j] = max(match, delete, insert)
    align1, align2 = '', ''
    i, j = m, n
    while i > 0 and j > 0:
        score_current = score[i][j]
        score_diagonal = score[i-1][j - 1]
        score_up = score[i][j - 1]
        score_left = score[i - 1][j]
        if score_current == score_diagonal + match_score(
         seq1[i-1], seq2[j-1], match_award, mismatch_penalty, gap_penalty
        ):
            align1 += seq1[i - 1]
            align2 += seq2[j - 1]
            i -= 1
            j -= 1
        elif score_current == score_left + gap_penalty:
            align1 += seq1[i - 1]
            align2 += '-'
            i -= 1
        elif score_current == score_up + gap_penalty:
            align1 += '-'
            align2 += seq2[j - 1]
            j -= 1
    while i > 0:
        align1 += seq1[i - 1]
        align2 += '-'
        i -= 1
    while j > 0:
        align1 += '-'
        align2 += seq2[j - 1]
        j -= 1
    return align1[::-1], align2[::-1]


def get_group_information(sites):
    pdbs = list(set([site.pdb for site in sites]))
    classifications = []
    keywords = []
    for pdb in pdbs:
        classifications.append(pdb.classification.upper())
        keywords += pdb.keywords.upper().split(", ")
    classifications = Counter(classifications)
    keywords = Counter(keywords)
    title_keywords = {}
    bad_keywords = ["INHIBITOR", "ZINC", "ZINC ENZYME"]
    for keyword in keywords:
        if keyword not in bad_keywords:
            count = 0
            for pdb in pdbs:
                if keyword in pdb.title: count += 1
            title_keywords[keyword] = count
    title_keywords = list(reversed(sorted(title_keywords.items(), key=lambda k: k[1])))
    cutoff = int(len(pdbs) * 0.25)
    classifications = [c for c, n in classifications.items() if n >= cutoff]
    keywords = [k for k, n in keywords.items() if n >= cutoff]
    if title_keywords:
        if title_keywords[0][0] in keywords:
            keywords.remove(title_keywords[0][0])
        keywords.insert(0, title_keywords[0][0])
    return ", ".join(keywords), ", ".join(classifications)


def get_spacers(sequence):
    spacers = []
    count = None
    for char in sequence:
        if count is not None: count += 1
        if char.istitle():
            if count is not None: spacers.append(str(count - 1))
            count = 0
    return ", ".join(spacers)



def dump_db_to_json():
    with open("data/zinc.json", "w") as f:
        sysout, sys.stdout = sys.stdout, f
        call_command("dumpdata",  "--exclude=contenttypes", verbosity=0)
    sys.stdout = sysout
