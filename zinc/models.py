"""Zinc models."""

from django.db import models

class Pdb(models.Model):
    """Represents a PDB structure file."""

    class Meta:
        db_table = "PDBs"

    id = models.CharField(primary_key=True, max_length=128)
    title = models.CharField(max_length=1024)
    classification = models.CharField(null=True, blank=True, max_length=1024)
    deposited = models.DateField(null=True, blank=True)
    resolution = models.FloatField(null=True, blank=True)
    organism = models.CharField(null=True, blank=True, max_length=1024)
    expression = models.CharField(null=True, blank=True, max_length=1024)
    technique = models.CharField(null=True, blank=True, max_length=1024)
    rfactor = models.FloatField(null=True, blank=True)
    skeleton = models.BooleanField()


    @staticmethod
    def create_from_atomium(pdb):
        """Creates a Pdb record from an atomium Pdb object."""

        from .utilities import model_is_skeleton
        return Pdb.objects.create(
         id=pdb.code, rfactor=pdb.rfactor, classification=pdb.classification,
         deposited=pdb.deposition_date, organism=pdb.organism, title=pdb.title,
         expression=pdb.expression_system, technique=pdb.technique,
         resolution=pdb.resolution, skeleton=model_is_skeleton(pdb.model),
        )


    @staticmethod
    def search(term):
        """Searches the Pdb objects with a term by looking for an exact match
        in IDs or a partial match in titles."""

        return Pdb.objects.filter(
         models.Q(id=term.upper()) | models.Q(title__contains=term.upper())
        ).order_by("-deposited")


    @property
    def ngl_metals_sele(self):
        return " or ".join([metal.residue.ngl_sele for metal in self.metal_set.all()])



class ZincSite(models.Model):
    """A zinc binding site, with one or more zinc atoms in it."""

    class Meta:
        db_table = "zinc_sites"

    id = models.CharField(primary_key=True, max_length=128)
    pdb = models.ForeignKey(Pdb, on_delete=models.CASCADE)

    @property
    def ngl_metals_sele(self):
        selectors = []
        for metal in self.metal_set.all():
            res = metal.residue
            selectors.append(
             res.ngl_sele
            )
        return " or ".join(selectors)


    @property
    def ngl_residues_sele(self):
        selectors = []
        for res in self.residue_set.all():
            selectors.append(
             res.ngl_side_chain_sele
            )
        return " or ".join(selectors)



class Chain(models.Model):
    """A chain of residues in a PDB."""

    class Meta:
        db_table = "chains"
        ordering = ["id"]

    id = models.CharField(primary_key=True, max_length=128)
    chain_pdb_identifier = models.CharField(max_length=128)
    sequence = models.TextField()
    pdb = models.ForeignKey(Pdb, on_delete=models.CASCADE)


    @staticmethod
    def create_from_atomium(chain, pdb):
        """Creates a chain record from an atomium Chain object and an existing
        Pdb record."""

        return Chain.objects.create(
         id=f"{pdb.id}{chain.id}", pdb=pdb,
         sequence = "".join([res.code for res in chain.residues()]),
         chain_pdb_identifier=chain.id
        )



class Residue(models.Model):
    "A collection of atoms, usually in a row on a chain."

    class Meta:
        db_table = "residues"
        ordering = ["residue_pdb_identifier"]

    id = models.CharField(primary_key=True, max_length=128)
    residue_pdb_identifier = models.IntegerField()
    insertion_pdb_identifier = models.CharField(max_length=128)
    name = models.CharField(max_length=128)
    site = models.ForeignKey(ZincSite, on_delete=models.CASCADE, null=True, blank=True)
    chain = models.ForeignKey(Chain, on_delete=models.CASCADE)


    @staticmethod
    def create_from_atomium(residue, chain, site=None):
        """Creates a residue record from an atomium Record object and existing
        ZincSite and Chain records. You must specify the residue number."""

        numeric_id = int("".join(
         c for c in residue.id if c.isdigit() or c == "-"
        ))
        insertion = residue.id[residue.id.find(str(numeric_id)) + len(str(numeric_id)):]
        id = f"{site.id}{residue.id}{residue.name}" if site else f"{chain.id}{residue.id}{residue.name}"
        residue_record = Residue.objects.create(
         id=id,
         residue_pdb_identifier=numeric_id,
         insertion_pdb_identifier=insertion,
         name=residue.name, chain=chain, site=site,
        )
        if site:
            for atom in residue.atoms():
                Atom.create_from_atomium(atom, residue_record)
        return residue_record


    @property
    def ngl_sele(self):
        return f"{self.residue_pdb_identifier}^{self.insertion_pdb_identifier}:{self.chain.chain_pdb_identifier}"


    @property
    def ngl_side_chain_sele(self):
        return f"(sidechain or .CA) and " + self.ngl_sele



class BaseAtom(models.Model):
    """The base class for residue atoms and metal atoms."""

    class Meta:
        abstract = True


    id = models.TextField(primary_key=True)
    atom_pdb_identifier = models.IntegerField()
    name = models.CharField(max_length=32)
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    element = models.CharField(max_length=8)
    charge = models.FloatField()
    bfactor = models.FloatField()
    residue = models.ForeignKey(Residue, on_delete=models.CASCADE)

    @staticmethod
    def create_from_atomium(cls, atom, residue):
        return cls(
         id=f"{residue.id}{atom.id}", atom_pdb_identifier=atom.id,
         name=atom.name, x=atom.x, y=atom.y, z=atom.z, charge=atom.charge,
         element=atom.element, bfactor=atom.bfactor, residue=residue
        )



class Atom(BaseAtom):
    """An atom belonging to some Residue."""

    class Meta:
        db_table = "atoms"

    liganding = models.BooleanField()


    @staticmethod
    def create_from_atomium(atom, residue):
        atom_record = BaseAtom.create_from_atomium(Atom, atom, residue)
        atom_record.liganding = atom.liganding
        atom_record.save()
        return atom_record



class Metal(BaseAtom):
    """A metal atom in a PDB - usually zinc but ocasionally other metals are
    cocatalytic with zinc."""

    class Meta:
        db_table = "metals"

    site = models.ForeignKey(ZincSite, on_delete=models.CASCADE)
    pdb = models.ForeignKey(Pdb, on_delete=models.CASCADE)


    @staticmethod
    def create_from_atomium(atom, pdb, site, chain):
        residue = Residue.create_from_atomium(atom.molecule, chain)
        atom = BaseAtom.create_from_atomium(Metal, atom, residue)
        atom.site, atom.pdb = site, pdb
        atom.save()
        return atom





'''class Pdb():





class Atom(BaseAtom):

    residue = models.ForeignKey(Residue, on_delete=models.CASCADE)


    @staticmethod
    def create_from_atomium(atom, residue):
        """Creates an atom record from an atomium Atom object and an existing
        Residue record. The atoms must have been given a liganding property at
        some point, as atomium atoms don't usually have this property."""

        return Atom.objects.create(
         id=f"{residue.id}{atom.id}", atom_pdb_identifier=atom.id, name=atom.name,
         x=atom.x, y=atom.y, z=atom.z, charge=atom.charge, bfactor=atom.bfactor,
         residue=residue, liganding=atom.liganding, element=atom.element,
        )



class Metal(Atom):
    """A metal atom in a PDB - usually zinc but ocasionally other metals are
    cocatalytic with zinc."""

    class Meta:
        db_table = "metals"

    site = models.ForeignKey(ZincSite, on_delete=models.CASCADE)
    pdb = models.ForeignKey(Pdb, on_delete=models.CASCADE)
    residue_id = models.CharField(max_length=32)
    chain_id = models.CharField(max_length=32)


    @staticmethod
    def create_from_atomium(atom, site):
        """Creates a metal record from an atomium Atom object and an existing
        ZincSite record."""

        return Metal.objects.create(
         id=f"{site.pdb.id}{atom.id}", atom_id=atom.id, x=atom.x, y=atom.y,
         z=atom.z, charge=atom.charge, bfactor=atom.bfactor, residue=None,
         liganding=atom.liganding, element=atom.element, name=atom.name,
         site=site, pdb=site.pdb, residue_id=
        )
'''
