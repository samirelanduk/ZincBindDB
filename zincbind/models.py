"""ZincBind models."""

from django.db import models

class Pdb(models.Model):
    """Represents a PDB structure file. There should be one for every PDB file
    ther is."""

    id = models.CharField(primary_key=True, max_length=64)
    title = models.TextField()
    deposited = models.DateField()
    resolution = models.FloatField()
    checked = models.DateField(blank=True, null=True)



class Residue(models.Model):
    """Represents a residue in the PDB sense - that is it can be an amino acid
    residue in a macromolecular chain, or it can be a small molecule such as
    water."""

    id = models.TextField(primary_key=True)
    residue_id = models.CharField(max_length=32)
    name = models.CharField(max_length=32)
    chain = models.CharField(max_length=16)
    number = models.IntegerField()
    pdb = models.ForeignKey(Pdb)
