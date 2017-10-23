import atomium
from .models import Pdb, ZincSite, Residue, Atom

def create_zinc_site(pdb, zinc, residues):
    """Creates a new ZincSite from atomium Pdb, Molecule, and Residues objects.
    Any components that don't exist will be created first."""

    pdb_record = create_pdb(pdb)
    residue_records = [create_residue(res, pdb_record) for res in residues]
    site = ZincSite.objects.create(pk=pdb_record.id + zinc.molecule_id())
    for residue in residue_records:
        site.residues.add(residue)
    return site


def create_manual_zinc_site(pdb_code, zinc_id, residue_ids):
    """Creates a new ZincSite from information passed in from the manual
    form."""

    pdb = atomium.fetch(pdb_code, pdbe=True)
    model = pdb.model()
    zinc = model.molecule(molecule_id=zinc_id)
    residues = [model.residue(residue_id=res_id) for res_id in residue_ids]
    return create_zinc_site(pdb, zinc, residues)


def create_pdb(pdb):
    """Creates a new Pdb record and returns the new object, from an atomium Pdb
    object. If a Pdb with this ID already exists, that is returned and nothing
    new is created."""

    existing_pdbs = Pdb.objects.filter(pk=pdb.code())
    if existing_pdbs: return existing_pdbs[0]
    return Pdb.objects.create(
     pk=pdb.code(), deposition_date=pdb.deposition_date(), title=pdb.title()
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
