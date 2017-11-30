"""Contains factory functions for creating objects in the database."""

from datetime import datetime
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
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

    try:
        return Pdb.objects.get(pk=pdb.code())
    except ObjectDoesNotExist:
        return Pdb.objects.create(
         pk=pdb.code(), deposited=pdb.deposition_date(), title=pdb.title(),
         resolution=pdb.resolution(), rfactor=pdb.rfactor(),
         classification=pdb.classification(), technique=pdb.technique(),
         organism=pdb.organism(), expression=pdb.expression_system(),
         checked=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )


def create_residue(residue, zinc_atom, site):
    """Creates a new Residue record and any associated Atom records, and returns
    it. If it already exists it will just be returned."""

    try:
        residue_id = residue.residue_id()
        chain = residue.chain().chain_id()
    except AttributeError:
        residue_id = residue.molecule_id()
        chain = None
    residue_pk = site.pk + residue_id
    try:
        return Residue.objects.get(pk=residue_pk)
    except ObjectDoesNotExist:
        residue_record = Residue.objects.create(
         pk=residue_pk, residue_id=residue_id, name=residue.name(),
         number=residue.chain().residues().index(residue) + 1 if chain else 10000,
         chain=chain, site=site
        )
        for atom in residue.atoms():
            Atom.objects.create(
             pk=residue_pk + str(atom.atom_id()), atom_id=atom.atom_id(),
             x = atom.x(), y=atom.y(), z=atom.z(), element=atom.element(),
             name=atom.name(), charge=atom.charge(), bfactor=atom.bfactor(),
             alpha=(atom.name() == "CA"), beta=(atom.name() == "CB"),
             liganding=(atom.distance_to(zinc_atom) <= 4 and atom.name() != "H"),
             residue=residue_record
            )
        return residue_record


def create_zinc_site(pdb, zinc, residues):
    """Creates a new ZincSite from atomium Pdb, Molecule, and Residues objects.
    Any components that don't exist will be created first."""

    pdb_record = create_pdb(pdb)
    try:
        atom = zinc.atom()
        site = ZincSite.objects.create(
         pk=pdb_record.id + zinc.molecule_id(),
         x=atom.x(), y=atom.y(), z=atom.z(),
         pdb=pdb_record
        )
    except IntegrityError: raise DuplicateSiteError
    residue_records = [create_residue(res, zinc.atom(), site) for res in residues]
    
    return site
