"""Zinc models."""

import subprocess
import json
from django.db import models

class Pdb(models.Model):
    """Represents a PDB structure file."""

    class Meta:
        db_table = "PDBs"

    id = models.CharField(primary_key=True, max_length=128)
    title = models.CharField(max_length=1024)
    classification = models.CharField(null=True, blank=True, max_length=1024)
    keywords = models.CharField(null=True, blank=True, max_length=2048)
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
         keywords=", ".join(pdb.keywords) if pdb.keywords else "",
         resolution=pdb.resolution, skeleton=model_is_skeleton(pdb.model),
        )


    @staticmethod
    def search(term):
        """Searches the Pdb objects with a term by looking for an exact match
        in IDs or a partial match in titles."""

        return Pdb.objects.filter(
         models.Q(id=term.upper()) | models.Q(title__contains=term.upper())
         | models.Q(classification__contains=term.upper())
         | models.Q(technique__contains=term.upper())
         | models.Q(organism__contains=term.upper())
         | models.Q(keywords__contains=term.upper())
        ).order_by("-deposited")


    @staticmethod
    def advanced_search(GET_dict):
        """Takes some GET data and uses it to search the PDBs."""

        qs = []
        string_terms = [
         "title", "classification", "keywords",
         "organism", "expression", "technique"
        ]
        for string_term in string_terms:
            if string_term in GET_dict:
                kwargs = {
                 string_term + "__contains": GET_dict[string_term].upper()
                }
                qs.append(models.Q(**kwargs))
        numeric_terms = [
         "resolution_gt", "resolution_lt", "rfactor_gt", "rfactor_lt",
         "deposited_gt", "deposited_lt"
        ]
        for numeric_term in numeric_terms:
            if numeric_term in GET_dict:
                kwargs = {
                 numeric_term.replace("_", "__"): GET_dict[numeric_term].upper()
                }
                qs.append(models.Q(**kwargs))
        return Pdb.objects.filter(*qs).order_by("-deposited")


    @staticmethod
    def blast_search(sequence):
        print(sequence)
        p = subprocess.Popen('echo "{}" | blastp -db data/chains.fasta -outfmt 15'.format(sequence), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = p.communicate()
        print(err)
        results = json.loads(out)["BlastOutput2"][0]["report"]["results"]["search"]["hits"]
        chain_ids = [r["description"][0]["title"].split("|")[1] for r in results]
        chains = sorted(Chain.objects.filter(id__in=chain_ids), key=lambda c: chain_ids.index(c.id))
        for chain, result in zip(chains, results):
            chain.blast_data = result["hsps"][0]
        return chains


    @property
    def metals(self):
        """Gets all the metal objects in this Pdb."""

        return Metal.objects.filter(residue__chain__pdb=self)


    @property
    def residues(self):
        """Gets all the residue objects that provide liganding atoms that belong
        to this Pdb (*not* those which are merely a container for a metal
        ion)."""

        return Residue.objects.filter(site__pdb=self)


    @property
    def ngl_metals_sele(self):
        """The NGL selector text needed to grab all metal atoms."""

        return " or ".join([metal.residue.ngl_sele for metal in self.metals])


    @property
    def ngl_residues_sele(self):
        """The NGL selector text needed to grab all binding residues."""

        return " or ".join([res.ngl_side_chain_sele for res in self.residues])



class ZincSite(models.Model):
    """A zinc binding site, with one or more zinc atoms in it."""

    class Meta:
        db_table = "zinc_sites"

    id = models.CharField(primary_key=True, max_length=128)
    pdb = models.ForeignKey(Pdb, on_delete=models.CASCADE)
    cluster = models.IntegerField(null=True, blank=True)

    @property
    def equivalent_sites(self):
        return ZincSite.objects.filter(cluster=self.cluster).exclude(id=self.id)


    @property
    def ngl_metals_sele(self):
        """The NGL selector text needed to grab all metal atoms in a site."""

        return " or ".join([
         metal.residue.ngl_sele for metal in self.metal_set.all()
        ])


    @property
    def ngl_residues_sele(self):
        """The NGL selector text needed to grab all binding residues in a
        site."""

        return " or ".join([
         res.ngl_side_chain_sele for res in self.residue_set.all()
        ])



class Chain(models.Model):
    """A chain of residues in a PDB."""

    class Meta:
        db_table = "chains"
        ordering = ["id"]

    id = models.CharField(primary_key=True, max_length=128)
    chain_pdb_identifier = models.CharField(max_length=128)
    sequence = models.TextField()
    pdb = models.ForeignKey(Pdb, on_delete=models.CASCADE)
    cluster = models.IntegerField(null=True, blank=True)


    @property
    def zincsites(self):
        residues = self.residue_set.all()
        sites = set(res.site for res in residues)
        return filter(bool, sites)


    @staticmethod
    def create_from_atomium(chain, pdb):
        """Creates a chain record from an atomium Chain object and an existing
        Pdb record."""

        return Chain.objects.create(
         id=f"{pdb.id}{chain.id}", pdb=pdb,
         sequence=chain.rep_sequence, chain_pdb_identifier=chain.id
        )



class Residue(models.Model):
    "A collection of atoms, usually in a row on a chain."

    class Meta:
        db_table = "residues"
        ordering = ["residue_pdb_identifier"]

    residue_pdb_identifier = models.IntegerField()
    insertion_pdb_identifier = models.CharField(max_length=128)
    name = models.CharField(max_length=128)
    site = models.ForeignKey(
     ZincSite, on_delete=models.CASCADE, null=True, blank=True
    )
    chain = models.ForeignKey(Chain, on_delete=models.CASCADE)


    @staticmethod
    def create_from_atomium(residue, chain, site=None):
        """Creates a residue record from an atomium Residue object and existing
        ZincSite and Chain records. You must specify the residue number."""

        numeric_id = int("".join(
         c for c in residue.id if c.isdigit() or c == "-"
        ))
        insertion = (residue.id[residue.id.find(str(numeric_id)) +
         len(str(numeric_id)):])
        residue_record = Residue.objects.create(
         residue_pdb_identifier=numeric_id,
         insertion_pdb_identifier=insertion,
         name=residue.name, chain=chain, site=site,
        )
        if site:
            for atom in residue.atoms():
                Atom.create_from_atomium(atom, residue_record)
        return residue_record


    @property
    def ngl_sele(self):
        """The NGL selector text needed to select the residue."""

        return (f"{self.residue_pdb_identifier}^" +
        f"{self.insertion_pdb_identifier}:{self.chain.chain_pdb_identifier}/0")


    @property
    def ngl_side_chain_sele(self):
        """The NGL selector text needed to select the residue side chain."""

        if self.name in ["HOH", "WAT"]:
            return self.ngl_sele
        return f"(sidechain or .CA) and " + self.ngl_sele


    @property
    def atomium_id(self):
        """Recreates the atomium ID of the residue."""

        return (f"{self.chain.chain_pdb_identifier}" +
        f"{self.residue_pdb_identifier}{self.insertion_pdb_identifier}")



class BaseAtom(models.Model):
    """The base class for residue atoms and metal atoms."""

    class Meta:
        abstract = True


    atom_pdb_identifier = models.IntegerField()
    name = models.CharField(max_length=32)
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    element = models.CharField(max_length=8)
    charge = models.FloatField()
    bfactor = models.FloatField()
    residue = models.ForeignKey(Residue, on_delete=models.CASCADE)

    @staticmethod
    def create_from_atomium(cls, atom, residue):
        return cls(
         atom_pdb_identifier=atom.id,
         name=atom.name, x=atom.x, y=atom.y, z=atom.z, charge=atom.charge,
         element=atom.element, bfactor=atom.bfactor, residue=residue
        )



class Atom(BaseAtom):
    """An atom belonging to some Residue."""

    class Meta:
        db_table = "atoms"

    liganding = models.BooleanField()


    @staticmethod
    def create_from_atomium(atom, residue):
        atom_record = BaseAtom.create_from_atomium(Atom, atom, residue)
        atom_record.liganding = atom.liganding
        atom_record.save()
        return atom_record



class Metal(BaseAtom):
    """A metal atom in a PDB - usually zinc but ocasionally other metals are
    cocatalytic with zinc."""

    class Meta:
        db_table = "metals"

    site = models.ForeignKey(ZincSite, on_delete=models.CASCADE)


    @staticmethod
    def create_from_atomium(atom, site, chain):
        residue = Residue.create_from_atomium(atom.ligand, chain)
        atom = BaseAtom.create_from_atomium(Metal, atom, residue)
        atom.site = site
        atom.save()
        return atom
