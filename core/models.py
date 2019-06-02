from django.db import models

class Pdb(models.Model):
    """Represents a PDB structure file."""

    class Meta:
        db_table = "PDBs"

    id = models.CharField(primary_key=True, max_length=32)
    title = models.CharField(max_length=1024)
    classification = models.CharField(null=True, blank=True, max_length=1024)
    keywords = models.CharField(null=True, blank=True, max_length=2048)
    deposition_date = models.DateField(null=True, blank=True)
    resolution = models.FloatField(null=True, blank=True)
    rvalue = models.FloatField(null=True, blank=True)
    organism = models.CharField(null=True, blank=True, max_length=1024)
    expression_system = models.CharField(null=True, blank=True, max_length=1024)
    technique = models.CharField(null=True, blank=True, max_length=1024)
    assembly = models.IntegerField(null=True, blank=True)
    skeleton = models.BooleanField()
