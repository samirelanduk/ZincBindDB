"""ZincBind models."""

from math import sqrt
from django.core.exceptions import ObjectDoesNotExist
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



class ZincSite(models.Model):
    """Represents a Zinc binding site."""

    id = models.TextField(primary_key=True)
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    pdb = models.ForeignKey(Pdb)

    @property
    def chain(self):
        return self.id[4]


    @property
    def number_id(self):
        return self.id[5:]



class Residue(models.Model):
    """Represents a residue in the PDB sense - that is it can be an amino acid
    residue in a macromolecular chain, or it can be a small molecule such as
    water."""

    id = models.TextField(primary_key=True)
    residue_id = models.CharField(max_length=32)
    name = models.CharField(max_length=32)
    chain = models.CharField(max_length=16, blank=True, null=True)
    number = models.IntegerField()
    site = models.ForeignKey(ZincSite)

    @property
    def number_id(self):
        return self.residue_id[1:]


    @property
    def full_name(self):
        return {
         "ALA": "Alanine", "ARG": "Arginine", "ASN": "Asparganine",
         "ASP": "Aspartic Acid", "CYS": "Cysteine", "GLU": "Glutamic Acid",
         "GLN": "Glutamine", "GLY": "Glycine", "HIS": "Histidine",
         "ILE": "Isoleucine", "LEU": "Leucine", "LYS": "Lysine",
         "MET": "Methionine", "PHE": "Phenylalanine", "PRO": "Proline",
         "SER": "Serine", "THR": "Threonine", "TRP": "Tryptophan",
         "TYR": "Tyrosine", "VAL": "Valine", "HOH": "Water"
        }.get(self.name, self.name)


    @property
    def ca(self):
        try:
            return self.atom_set.get(alpha=True)
        except ObjectDoesNotExist: return None


    @property
    def cb(self):
        try:
            return self.atom_set.get(beta=True)
        except ObjectDoesNotExist: return None



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

    @property
    def zinc_distance(self):
        site = self.residue.site
        return sqrt(
         ((self.x - site.x) ** 2) + 
         ((self.y - site.y) ** 2) + 
         ((self.z - site.z) ** 2)
        )
