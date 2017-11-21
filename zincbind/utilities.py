import requests
import re
import os
import atomium
from .exceptions import RcsbError, AtomiumError
from .models import Pdb

def get_all_pdb_codes():
    """Gets a list of all current PDB IDs, by querying the RCSB web services.

    :rtype: ``list``"""

    response = requests.get("https://www.rcsb.org/pdb/rest/getCurrent")
    if response.status_code != 200:
        raise RcsbError("RCSB returned an error when asked for all PDB codes")
    pattern = r"structureId=\"(.+?)\""
    pdbs = re.findall(pattern, response.text)
    if not pdbs:
        raise RcsbError("Could not parse PDB codes from RCSB's response")
    return pdbs


def remove_checked_pdbs(pdbs):
    """Takes a list of PDB codes and removes those which are already in the
    database. The list is changed in place and nothing is returned."""

    checked_pdb_codes = set(Pdb.objects.all().values_list("id", flat=True))
    for code in checked_pdb_codes:
        try:
            pdbs.remove(code)
        except ValueError: pass


def get_pdb_filestring(pdb_code):
    """Gets the text of a PDB file from a PDB code - first by trying to get the
    file locally, then by fetching from RCSB."""

    if "PDBPATH" in os.environ:
        try:
            with open(os.path.sep.join([
             os.environ["PDBPATH"], "pdb{}.ent".format(pdb_code.lower())
            ])) as f:
                return f.read()
        except FileNotFoundError: pass
    filestring = atomium.files.utilities.fetch_string(pdb_code)
    if filestring:
        return filestring
    else:
        raise RcsbError("Could not get PDB {} from RCSB".format(pdb_code))


def zinc_in_pdb(pdb_filestring):
    """Takes the text of a .pdb file and determines whether or not it contains a
    Zinc molecule, using a regular expression.

    :rtype: ``bool``"""

    return bool(re.search(r"HET\s+ZN\s+", pdb_filestring))


def get_pdb(pdb_filestring):
    """Gets an atomium ``Pdb`` object from a PDB filestring.

    :rtype: ``Pdb``"""

    try:
        d = atomium.files.pdbstring2pdbdict.pdb_string_to_pdb_dict(pdb_filestring)
        return atomium.files.pdbdict2pdb.pdb_dict_to_pdb(d)
    except:
        raise AtomiumError(
         "There was a problem parsing filestring with atomium"
        )


def model_is_skeleton(model):
    """Returns ``True`` if the model given only contains backbone atoms.

    :rtype: ``bool``"""

    for chain in model.chains():
        atom_names = set([atom.name() for atom in chain.atoms()])
        for name in atom_names:
            if name not in ["C", "N", "CA", "O"]:
                return False
    return True
