"""Contains factory functions for creating objects in the database."""

from datetime import datetime
from django.db import IntegrityError
from .models import Pdb, Residue, Atom, ZincSite
from .exceptions import DuplicateSiteError

def create_empty_pdb(pdb_code):
    """Adds a PDB code to the Pdb table, for those that have been checked and
    found to contain nothing relevant."""

    Pdb.objects.create(
     id=pdb_code, checked=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )


def create_pdb(pdb):
    """Creates a new Pdb record and returns the new object, from an atomium Pdb
    object. If a Pdb with this ID already exists, that is returned and nothing
    new is created."""

    existing_pdbs = Pdb.objects.filter(pk=pdb.code())
    if existing_pdbs: return existing_pdbs[0]
    return Pdb.objects.create(
     pk=pdb.code(), deposited=pdb.deposition_date(), title=pdb.title(),
     resolution=pdb.resolution(),
     checked=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )


def create_residue(residue, pdb_record):
    """Creates a new Residue record and any associated Atom records, and returns
    it. If it already exists it will just be returned."""

    residue_pk = pdb_record.id + residue.residue_id()
    existing_residues = Residue.objects.filter(pk=residue_pk)
    if existing_residues: return existing_residues[0]
    residue_record = Residue.objects.create(
     pk=residue_pk, residue_id=residue.residue_id(), name=residue.name(),
     number=residue.chain().residues().index(residue) + 1,
     chain=residue.chain().chain_id(), pdb=pdb_record
    )
    for atom in residue.atoms():
        Atom.objects.create(
         pk=pdb_record.id + str(atom.atom_id()), atom_id=atom.atom_id(),
         x = atom.x(), y=atom.y(), z=atom.z(), element=atom.element(),
         name=atom.name(), charge=atom.charge(), bfactor=atom.bfactor(),
         residue=residue_record
        )
    return residue_record


def create_zinc_site(pdb, zinc, residues):
    """Creates a new ZincSite from atomium Pdb, Molecule, and Residues objects.
    Any components that don't exist will be created first."""

    pdb_record = create_pdb(pdb)
    residue_records = [create_residue(res, pdb_record) for res in residues]
    try:
        atom = zinc.atom()
        site = ZincSite.objects.create(
         pk=pdb_record.id + zinc.molecule_id(),
         x=atom.x(), y=atom.y(), z=atom.z()
        )
    except IntegrityError: raise DuplicateSiteError
    for residue in residue_records:
        site.residues.add(residue)
    return site
