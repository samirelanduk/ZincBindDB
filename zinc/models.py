"""Zinc models."""

from django.db import models

class Pdb(models.Model):
    """Represents a PDB structure file."""

    class Meta:
        db_table = "PDBs"

    id = models.CharField(primary_key=True, max_length=128)
    title = models.CharField(max_length=1024)
    classification = models.CharField(max_length=1024)
    deposited = models.DateField()
    resolution = models.FloatField()
    organism = models.CharField(max_length=1024)
    expression = models.CharField(max_length=1024)
    technique = models.CharField(max_length=1024)
    rfactor = models.FloatField()
    skeleton = models.BooleanField()
    checked = models.DateTimeField()
