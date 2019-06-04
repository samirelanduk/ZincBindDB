from core.models import *

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


def create_site_record(site_dict, pdb_record, index):
    # Create site record itself
    from utilities import create_site_family
    return ZincSite.objects.create(
     id=f"{pdb_record.id}-{index}",
     family=create_site_family(site_dict["residues"]), pdb=pdb_record,
     residue_names="".join(set([f".{r.name}." for r in site_dict["residues"]]))
    )

    # Create metals
    metals = {}
    for metal in site["metals"].keys():
        metals[metal.id] = create_metal_record(metal, pdb_record)
    
    # Create chain interactions
    for chain in chains:
        sequence = get_chain_sequence(chain, site["residues"])
        create_chain_interaction_record(
            chain_dict[chain.id], site_record, sequence
        )
    
    # Create residue records
    atoms = {}
    for res in site["residues"]:
        chain_record = chain_dict[res.chain.id] if isinstance(res, atomium.Residue) else None
        create_residue_record(res, chain_record, site_record)


def create_chain_interaction_record(chain_record, site_record, sequence):
    return ChainInteraction.objects.create(
     sequence=sequence, chain=chain_record, site=site_record
    )


def create_residue_record(residue, chain_record, site_record):
    numeric_id, insertion = residue.id.split(".")[1], ""
    while not numeric_id[-1].isdigit():
        insertion += numeric_id[-1]
        numeric_id = numeric_id[:-1]
    numeric_id = int(numeric_id)
    signature = []
    if isinstance(residue, atomium.Residue):
        if residue.previous: signature = [residue.previous.name.lower()]
        signature.append(residue.name)
        if residue.next: signature.append(residue.next.name.lower())
    signature = ".".join(signature)
    residue_record = Residue.objects.create(
     residue_number=numeric_id, chain_identifier=residue.chain.id,
     insertion_code=insertion, chain_signature=signature,
     name=residue.name, chain=chain_record, site=site_record, atomium_id=residue.id
    )
    return residue_record
