"""Contains functions for building objects in the database."""

from core.models import *
from chains import get_chain_sequence
from sites import get_group_information, create_site_family

def create_pdb_record(pdb, assembly_id):
    """Creates a Pdb record from an atomium File and an assembly ID."""

    from utilities import model_is_skeleton
    return Pdb.objects.create(
     id=pdb.code, rvalue=pdb.rvalue, classification=pdb.classification,
     deposition_date=pdb.deposition_date, organism=pdb.source_organism,
     expression_system=pdb.expression_system, technique=pdb.technique,
     keywords=", ".join(pdb.keywords) if pdb.keywords else "", title=pdb.title,
     resolution=pdb.resolution, skeleton=model_is_skeleton(pdb.model),
     assembly=assembly_id
    )


def create_metal_record(atom, pdb_record, site_record=None, omission=None):
    """Creates a Metal record. You specify a Pdb record, and optionally either
    a Site record (if part of one) or a reason for omission (if not)."""

    residue = atom.het
    numeric_id, insertion = residue.id.split(".")[1], ""
    while not numeric_id[-1].isdigit():
        insertion += numeric_id[-1]
        numeric_id = numeric_id[:-1]
    numeric_id = int(numeric_id)
    x, y, z = atom.location
    return Metal.objects.create(
     atomium_id=atom.id, element=atom.element, name=atom.name, x=x, y=y, z=z, 
     residue_number=numeric_id, insertion_code=insertion,
     chain_id=atom.chain.id, residue_name=residue.name,
     pdb=pdb_record, site=site_record, omission_reason=omission
    )


def create_chain_record(chain, pdb_record, sequence):
    """Creates a Chain record from an atomium Chain, a Pdb record, and a
    sequence."""

    return Chain.objects.create(
     id=f"{pdb_record.id}{chain.id}", pdb=pdb_record,
     sequence=sequence, atomium_id=chain.id
    )


def create_site_record(site_dict, pdb_record, index, chains_dict):
    """Creates a ZincSite record and all its sub-components from a dictionary
    representing its metals, residues and chains. The ID will be created from
    the index provided, and the chain information from the chain dictionary
    provided."""

    # Create site record itself
    residue_names = set([f".{r.name}." for r in site_dict["residues"]])
    residue_names = sorted(list(residue_names))
    site_record = ZincSite.objects.create(
     id=f"{pdb_record.id}-{index}",
     family=create_site_family(site_dict["residues"]), pdb=pdb_record,
     residue_names="".join(residue_names)
    )

    # Create metals
    metals_dict = {}
    for metal in sorted(site_dict["metals"].keys(), key=lambda m: m.id):
        metals_dict[metal.id] = create_metal_record(metal, pdb_record, site_record)
    
    # Create chain interactions
    for chain in sorted(site_dict["chains"], key=lambda c: c.id):
        sequence = get_chain_sequence(chain, site_dict["residues"])
        create_chain_interaction_record(
         chains_dict[chain.id], site_record, sequence
        )
    
    # Create residue records
    atoms_dict = {}
    for res in sorted(site_dict["residues"], key=lambda r: r.id):
        chain_record = chains_dict[res.chain.id] if isinstance(res, atomium.Residue) else None
        create_residue_record(res, chain_record, site_record, atoms_dict)
    
    # Create bond records
    for metal, atoms in sorted(site_dict["metals"].items(), key=lambda a: a[0].id):
        for atom in sorted(atoms, key=lambda a: a.id):
            CoordinateBond.objects.create(
             metal=metals_dict[metal.id], atom=atoms_dict[atom]
            )
    
    return site_record


def create_chain_interaction_record(chain_record, site_record, sequence):
    """Creates a ChainInteraction record from the information provided."""

    return ChainInteraction.objects.create(
     sequence=sequence, chain=chain_record, site=site_record
    )


def create_residue_record(residue, chain_record, site_record, atoms_dict):
    """Creates a Residue record along with its atoms, from information given. A
    dictionary of atoms must be given to make coordinate bonds later."""

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
    for atom in sorted(residue.atoms(), key=lambda a: a.id):
        atoms_dict[atom] = create_atom_record(atom, residue_record)
    return residue_record


def create_atom_record(atom, residue_record):
    """Creates an Atom record from the information provided."""

    x, y, z = atom.location
    return Atom.objects.create(
     atomium_id=atom.id, name=atom.name, x=x, y=y, z=z,
     element=atom.element, residue=residue_record
    )


def create_chain_cluster_record(chain_ids, dates):
    """Creates a ChainCluster record from the information provided. All chains
    will be updated as required."""

    dates = [dates[id] for id in chain_ids]
    id = chain_ids[dates.index(min(dates))]
    cluster_object = ChainCluster.objects.create(id=id)
    for chain_id in chain_ids:
        chain = Chain.objects.get(id=chain_id)
        chain.cluster = cluster_object
        chain.save()


def create_group_record(sites):
    """Creates a Group record from the information provided. All relevant sites
    will be updated."""

    oldest = sorted(sites, key=lambda s: s.date)[0]
    keywords, classifications = get_group_information(sites)
    group = Group.objects.create(
     id=oldest.id, family=sites[0].family,
     keywords=keywords, classifications=classifications
    )
    for site in sites:
        site.group = group
        if site.id == group.id: site.representative = True
        site.save()

