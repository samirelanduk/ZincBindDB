from .models import Pdb

def create_pdb(pdb):
    """Creates a new Pdb record and returns the new object, from an atomium Pdb
    object. If a Pdb with this ID already exists, that is returned and nothing
    new is created."""
    
    existing_pdbs = Pdb.objects.filter(pk=pdb.code())
    if existing_pdbs: return existing_pdbs[0]
    return Pdb.objects.create(
     pk=pdb.code(), deposition_date=pdb.deposition_date(), title=pdb.title()
    )
