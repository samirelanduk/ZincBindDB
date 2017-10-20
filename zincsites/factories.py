from .models import Pdb, ZincSite

def create_zinc_site(pdb, zinc, residues):
    """Creates a new ZincSite from atomium Pdb, Molecule, and Residues objects.
    Any components that don't exist will be created first."""
    
    pdb_record = create_pdb(pdb)
    residue_records = [create_residue(res, pdb_record) for res in residues]
    site = ZincSite.objects.create(pk=pdb_record.id + zinc.molecule_id())
    for residue in residue_records:
        site.residues.add(residue)
    return site


def create_pdb(pdb):
    """Creates a new Pdb record and returns the new object, from an atomium Pdb
    object. If a Pdb with this ID already exists, that is returned and nothing
    new is created."""

    existing_pdbs = Pdb.objects.filter(pk=pdb.code())
    if existing_pdbs: return existing_pdbs[0]
    return Pdb.objects.create(
     pk=pdb.code(), deposition_date=pdb.deposition_date(), title=pdb.title()
    )


def create_residue():
    pass
