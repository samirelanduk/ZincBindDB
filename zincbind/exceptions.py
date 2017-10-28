class RcsbError(Exception):
    """The exception raised if there is some problem interacting with the RCSB
    web services."""
    pass



class AtomiumError(Exception):
    """The exception raised if there is some problem parsing PDBs with
    the atomium library."""
    pass
