from core.models import Pdb, Metal, Chain

def create_pdb_record(pdb, assembly_id):
    from utilities import model_is_skeleton
    return Pdb.objects.create(
     id=pdb.code, rvalue=pdb.rvalue, classification=pdb.classification,
     deposition_date=pdb.deposition_date, organism=pdb.source_organism,
     expression_system=pdb.expression_system, technique=pdb.technique,
     keywords=", ".join(pdb.keywords) if pdb.keywords else "", title=pdb.title,
     resolution=pdb.resolution, skeleton=model_is_skeleton(pdb.model),
     assembly=assembly_id
    )


def create_metal_record(atom, pdb_record, omission=None):
    residue = atom.structure
    numeric_id, insertion = residue.id.split(".")[1], ""
    while not numeric_id[-1].isdigit():
        insertion += numeric_id[-1]
        numeric_id = numeric_id[:-1]
    numeric_id = int(numeric_id)
    return Metal.objects.create(
     atomium_id=atom.id, element=atom.element, name=atom.name, x=atom.x,
     y=atom.y, z=atom.z, residue_number=numeric_id, insertion_code=insertion,
     chain_id=atom.chain.id, residue_name=residue.name,
     pdb=pdb_record, omission_reason=omission
    )


def create_chain_record(chain, pdb_record, sequence):
    return Chain.objects.create(
     id=f"{pdb_record.id}{chain.id}", pdb=pdb_record,
     sequence=sequence, atomium_id=chain.id
    )
