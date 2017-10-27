from django.db import models

class Pdb(models.Model):

    id = models.TextField(primary_key=True)
    title = models.TextField()
    deposited = models.DateField()
    resolution = models.FloatField()
    checked = models.DateField(blank=True, null=True)
