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
        return Pdb.objects.filter(
         models.Q(id=term.upper()) | models.Q(title__contains=term.upper())
        ).order_by("-deposited")



class Chain(models.Model):
    """A chain of residues in a PDB."""

    class Meta:
        db_table = "chains"
        ordering = ["id"]

    id = models.CharField(primary_key=True, max_length=128)
    sequence = models.TextField()
    pdb = models.ForeignKey(Pdb, on_delete=models.CASCADE)


    @staticmethod
    def create_from_atomium(chain, pdb):
        """Creates a chain record from an atomium Chain object and an existing
        Pdb record."""

        return Chain.objects.create(
         id=f"{pdb.id}{chain.id}", pdb=pdb,
         sequence = "".join([res.code for res in chain.residues()])
        )



class ZincSite(models.Model):
    """A zinc binding site, with one or more zinc atoms in it."""

    class Meta:
        db_table = "zinc_sites"

    id = models.CharField(primary_key=True, max_length=128)
    pdb = models.ForeignKey(Pdb, on_delete=models.CASCADE)




class Metal(models.Model):
    """A metal atom in a PDB - usually zinc but ocasionally other metals are
    cocatalytic with zinc."""

    class Meta:
        db_table = "metals"

    id = models.CharField(primary_key=True, max_length=128)
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    element = models.CharField(max_length=8)
    site = models.ForeignKey(ZincSite, on_delete=models.CASCADE)

    @staticmethod
    def create_from_atomium(atom, site):
        """Creates a metal record from an atomium Atom object and an existing
        ZincSite record."""

        return Metal.objects.create(
         id=f"{site.pdb.id}{atom.id}", x=atom.x, y=atom.y, z=atom.z, site=site,
         element=atom.element
        )



class Residue(models.Model):
    """A zinc atom in a PDB."""

    class Meta:
        db_table = "residues"

    id = models.CharField(primary_key=True, max_length=128)
    number = models.IntegerField()
    residue_id = models.CharField(max_length=128)
    name = models.CharField(max_length=128)
    site = models.ForeignKey(ZincSite, on_delete=models.CASCADE)
    chain = models.ForeignKey(Chain, on_delete=models.CASCADE, null=True)


    @staticmethod
    def create_from_atomium(residue, site, chain, number):
        """Creates a residue record from an atomium Record object and existing
        ZincSite and Chain records. You must specify the residue number."""

        residue_record = Residue.objects.create(
         id=f"{site.pdb.id}{residue.id}{residue.name}", number=number,
         chain=chain, site=site, residue_id=residue.id, name=residue.name
        )
        for atom in residue.atoms():
            Atom.create_from_atomium(atom, residue_record)
        return residue_record



class Atom(models.Model):
    """An atom belonging to some Residue."""

    class Meta:
        db_table = "atoms"

    id = models.TextField(primary_key=True)
    atom_id = models.IntegerField()
    name = models.CharField(max_length=32)
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    element = models.CharField(max_length=8)
    charge = models.FloatField()
    bfactor = models.FloatField()
    liganding = models.BooleanField()
    residue = models.ForeignKey(Residue, on_delete=models.CASCADE)


    @staticmethod
    def create_from_atomium(atom, residue):
        """Creates an atom record from an atomium Atom object and an existing
        Residue record. The atoms must have been given a liganding property at
        some point, as atomium atoms don't usually have this property."""

        return Atom.objects.create(
         id=f"{residue.id}{atom.id}", atom_id=atom.id, x=atom.x, y=atom.y,
         z=atom.z, charge=atom.charge, bfactor=atom.bfactor, residue=residue,
         liganding=atom.liganding, element=atom.element, name=atom.name,
        )
