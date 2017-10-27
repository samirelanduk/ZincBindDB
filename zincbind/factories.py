"""Contains factory functions for creating objects in the database."""

from datetime import datetime
from .models import Pdb

def create_empty_pdb(pdb_code):
    """Adds a PDB code to the Pdb table, for those that have been checked and
    found to contain nothing relevant."""

    Pdb.objects.create(
     id=pdb_code, checked=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
