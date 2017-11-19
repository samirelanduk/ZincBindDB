"""ZincBind models."""

from django.db import models

class Pdb(models.Model):
    """Represents a PDB structure file. There should be one for every PDB file
    ther is."""

    id = models.CharField(primary_key=True, max_length=64)
    title = models.TextField(blank=True, null=True)
    classification = models.TextField(blank=True, null=True)
    deposited = models.DateField(blank=True, null=True)
    resolution = models.FloatField(blank=True, null=True)
    organism = models.TextField(blank=True, null=True)
    expression = models.TextField(blank=True, null=True)
    technique = models.TextField(blank=True, null=True)
    rfactor = models.FloatField(blank=True, null=True)
    checked = models.DateTimeField()



class Residue(models.Model):
    """Represents a residue in the PDB sense - that is it can be an amino acid
    residue in a macromolecular chain, or it can be a small molecule such as
    water."""

    id = models.TextField(primary_key=True)
    residue_id = models.CharField(max_length=32)
    name = models.CharField(max_length=32)
    chain = models.CharField(max_length=16, blank=True, null=True)
    number = models.IntegerField()



class ZincSite(models.Model):
    """Represents a Zinc binding site."""

    id = models.TextField(primary_key=True)
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    pdb = models.ForeignKey(Pdb)
    residues = models.ManyToManyField(Residue)



class Atom(models.Model):
    """Represents an Atom from a PDB."""

    id = models.TextField(primary_key=True)
    atom_id = models.IntegerField()
    name = models.CharField(max_length=32)
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    element = models.CharField(max_length=8)
    charge = models.FloatField()
    bfactor = models.FloatField()
    alpha = models.BooleanField()
    beta = models.BooleanField()
    liganding = models.BooleanField()
    residue = models.ForeignKey(Residue)
