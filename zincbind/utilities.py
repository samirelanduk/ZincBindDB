import requests
import re
from .exceptions import RcsbError

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
