from django.db import models

class Pdb(models.Model):

    id = models.TextField(primary_key=True)
    title = models.TextField()
    deposition_date = models.DateField()



class Residue(models.Model):

    class Meta:
        ordering = ["chain", "number"]

    id = models.TextField(primary_key=True)
    residue_id = models.TextField()
    number = models.IntegerField()
    chain = models.TextField()
    name = models.TextField()
    pdb = models.ForeignKey(Pdb)


class ZincSite(models.Model):

    id = models.TextField(primary_key=True)
    residues = models.ManyToManyField(Residue)

    @property
    def pdb(self):
        return self.residues.first().pdb
