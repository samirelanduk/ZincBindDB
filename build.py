#! /usr/bin/env python3

import requests

def get_zinc_pdb_codes():
    """Gets PDB codes for all structures with a zinc atom in them.
    If the response returned has an error code of 500, or if there are fewer
    than 10,000 PDB codes sent back, an error will be thrown."""

    query = "<orgPdbQuery>"\
    "<queryType>org.pdb.query.simple.ChemCompFormulaQuery</queryType>"\
    "<formula>ZN</formula></orgPdbQuery>"
    url = "https://www.rcsb.org//pdb/rest/search/"
    response = requests.post(url, data=query.encode(), headers={
     "Content-Type": "application/x-www-form-urlencoded"
    })
    if response.status_code == 200:
        codes = response.text.split()
        if len(codes) > 10000:
            return response.text.split()
    raise Exception("RCSB didn't send back PDB codes")


def main():
    # What PDBs have zinc in them?
    codes = get_zinc_pdb_codes()
    print(f"There are {len(codes)} PDB codes")
    

print()
main()
print()
