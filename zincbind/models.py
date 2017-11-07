"""ZincBind models."""

from django.db import models

class Pdb(models.Model):
    """Represents a PDB structure file. There should be one for every PDB file
    ther is."""

    id = models.CharField(primary_key=True, max_length=64)
    title = models.TextField(blank=True, null=True)
    deposited = models.DateField(blank=True, null=True)
    resolution = models.FloatField(blank=True, null=True)
    checked = models.DateTimeField()

    @property
    def sites(self):
        return set([residue.zincsite_set.first() for residue in self.residue_set.all()])



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
    residue = models.ForeignKey(Residue)



class ZincSite(models.Model):
    """Represents a Zinc binding site."""

    id = models.TextField(primary_key=True)
    residues = models.ManyToManyField(Residue)
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
