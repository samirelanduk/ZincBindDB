import atomium
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



class Metal(models.Model):
    """A metal atom - usually zinc."""

    class Meta:
        db_table = "metals"

    atomium_id = models.IntegerField()
    name = models.CharField(max_length=32)
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    element = models.CharField(max_length=8)
    residue_name = models.CharField(max_length=32)
    residue_number = models.IntegerField()
    insertion_code = models.CharField(max_length=128)
    chain_id = models.CharField(max_length=128)
    omission_reason = models.TextField(blank=True, null=True)
    pdb = models.ForeignKey(Pdb, on_delete=models.CASCADE)



class Chain(models.Model):
    """A chain of residues in a PDB."""

    class Meta:
        db_table = "chains"
        ordering = ["id"]

    id = models.CharField(primary_key=True, max_length=128)
    atomium_id = models.CharField(max_length=128)
    sequence = models.TextField()
    pdb = models.ForeignKey(Pdb, on_delete=models.CASCADE)



class ZincSite(models.Model):
    """A zinc binding site, with one or more zinc atoms in it."""

    class Meta:
        db_table = "zinc_sites"

    id = models.CharField(primary_key=True, max_length=128)
    family = models.CharField(max_length=128)
    residue_names = models.CharField(max_length=512)
    representative = models.BooleanField(default=False)
    pdb = models.ForeignKey(Pdb, on_delete=models.CASCADE)



class ChainInteraction(models.Model):
    """An interaction between a chain and a zinc binding sites."""

    class Meta:
        db_table = "chain_interactions"

    sequence = models.TextField()
    chain = models.ForeignKey(Chain, on_delete=models.CASCADE, blank=True, null=True)
    site = models.ForeignKey(ZincSite, on_delete=models.CASCADE, blank=True, null=True)



class Residue(models.Model):
    "A collection of atoms, usually in a row on a chain."

    class Meta:
        db_table = "residues"
        ordering = ["residue_number"]

    residue_number = models.IntegerField()
    insertion_code = models.CharField(max_length=128)
    name = models.CharField(max_length=128)
    atomium_id = models.CharField(max_length=128)
    chain_identifier = models.CharField(max_length=128)
    chain_signature = models.CharField(max_length=128, blank=True)
    site = models.ForeignKey(ZincSite, on_delete=models.CASCADE)
    chain = models.ForeignKey(Chain, blank=True, null=True, on_delete=models.CASCADE)
    
