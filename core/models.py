"""Zinc models."""

import subprocess
import json
from collections import Counter
from datetime import datetime
from atomium.data import CODES
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
    assembly = models.IntegerField(null=True, blank=True)
    skeleton = models.BooleanField()


    @staticmethod
    def create_from_atomium(pdb, assembly_id):
        """Creates a Pdb record from an atomium Pdb object."""

        from .utilities import model_is_skeleton
        return Pdb.objects.create(
         id=pdb.code, rfactor=pdb.rvalue, classification=pdb.classification,
         deposited=pdb.deposition_date, organism=pdb.source_organism, title=pdb.title,
         expression=pdb.expression_system, technique=pdb.technique,
         keywords=", ".join(pdb.keywords) if pdb.keywords else "",
         resolution=pdb.resolution, skeleton=model_is_skeleton(pdb.model),
         assembly=assembly_id
        )


    @property
    def residues(self):
        """Gets all the residue objects that provide liganding atoms that belong
        to this Pdb."""

        return Residue.objects.filter(site__pdb=self)


    @property
    def omitted_metals(self):
        """Gets all the metal objects that have no ZincSite in this Pdb"""

        return Metal.objects.filter(pdb=self).exclude(omission=None)


    @property
    def ngl_metals_sele(self):
        """The NGL selector text needed to grab all metal atoms in the PDB."""

        return " or ".join([metal.ngl_sele for metal in self.metal_set.all()])


    @property
    def ngl_residues_sele(self):
        """The NGL selector text needed to grab all binding residues."""

        return " or ".join([res.ngl_side_chain_sele for res in self.residues])



class Group(models.Model):
    """A collection of equivalent zinc sites."""

    class Meta:
        db_table = "groups"

    id = models.CharField(primary_key=True, max_length=128)
    family = models.CharField(max_length=128)
    keywords = models.CharField(max_length=1024)
    classifications = models.CharField(max_length=1024)

    @property
    def keywords_list(self):
        return self.keywords.split(", ")


    @property
    def classifications_list(self):
        return self.classifications.split(", ")



class ZincSite(models.Model):
    """A zinc binding site, with one or more zinc atoms in it."""

    class Meta:
        db_table = "zinc_sites"

    id = models.CharField(primary_key=True, max_length=128)
    family = models.CharField(max_length=128)
    residue_names = models.CharField(max_length=512)
    copies = models.IntegerField()
    representative = models.BooleanField(default=False)
    group = models.ForeignKey(
     Group, on_delete=models.SET_NULL, null=True, blank=True
    )
    pdb = models.ForeignKey(Pdb, on_delete=models.CASCADE)

    @staticmethod
    def search(term, sort):
        """Searches the ZincSite objects with a term by looking for an exact
        match in PDB IDs or a partial match in PDB titles."""

        sites = ZincSite.objects.filter(
         models.Q(pdb__id=term.upper()) | models.Q(pdb__title__contains=term.upper())
         | models.Q(pdb__classification__contains=term.upper())
         | models.Q(pdb__technique__contains=term.upper())
         | models.Q(pdb__organism__contains=term.upper())
         | models.Q(pdb__keywords__contains=term.upper())
        ).order_by(sort, "pdb__id").annotate(
         pdb_id=models.F("pdb__id"),
         deposited=models.F("pdb__deposited"),
         species=models.F("pdb__organism"),
         title=models.F("pdb__title"),
         classification=models.F("pdb__classification"),
         technique=models.F("pdb__technique"),
         resolution=models.F("pdb__resolution"),
         residue_count=models.Count("residue")
        )
        pdbs, pdb = [], []
        for site in sites:
            if pdb and site.pdb_id != pdb[-1].pdb_id:
                pdbs.append(pdb)
                pdb = []
            pdb.append(site)
        if pdb: pdbs.append(pdb)
        return pdbs


    @staticmethod
    def advanced_search(GET_dict, sort):
        """Takes some GET data and uses it to search the PDBs."""

        qs = []
        string_terms = [
         "title", "classification", "keywords", "residue_names",
         "organism", "expression", "technique", "family", "code"
        ]
        for string_term in string_terms:
            if string_term in GET_dict:
                value = GET_dict[string_term].upper()
                if string_term == "family":
                    key = string_term
                elif string_term == "residue_names":
                    key = string_term + "__contains"
                    value = f".{value}."
                elif string_term == "code":
                    key = "family__contains"
                else:
                    key = "pdb__" + string_term + "__icontains"
                kwargs = {
                 key: value
                }
                qs.append(models.Q(**kwargs))
        numeric_terms = [
         "resolution_gt", "resolution_lt", "rfactor_gt", "rfactor_lt",
         "deposited_gt", "deposited_lt"
        ]
        for numeric_term in numeric_terms:
            if numeric_term in GET_dict:
                try:
                    float(GET_dict[numeric_term])
                except ValueError:
                    try:
                        datetime.strptime(GET_dict[numeric_term], "%Y-%m-%d")
                    except:
                        return []
                kwargs = {
                 "pdb__" + numeric_term.replace("_", "__"): GET_dict[numeric_term]
                }
                qs.append(models.Q(**kwargs))
        sites = ZincSite.objects.filter(*qs).order_by(sort, "pdb__id").annotate(
         pdb_id=models.F("pdb__id"),
         deposited=models.F("pdb__deposited"),
         species=models.F("pdb__organism"),
         title=models.F("pdb__title"),
         classification=models.F("pdb__classification"),
         technique=models.F("pdb__technique"),
         resolution=models.F("pdb__resolution"),
         residue_count=models.Count("residue")
        )
        pdbs, pdb = [], []
        for site in sites:
            if pdb and site.pdb_id != pdb[-1].pdb_id:
                pdbs.append(pdb)
                pdb = []
            pdb.append(site)
        if pdb: pdbs.append(pdb)
        return pdbs


    @property
    def equivalent_sites(self):
        """Returns other ZincSites in this cluster, or None if there aren't
        any."""

        if self.group:
            return self.group.zincsite_set.exclude(id=self.id)


    @property
    def coordinatebonds(self):
        return CoordinateBond.objects.filter(metal__site=self)


    @property
    def ngl_metals_sele(self):
        """The NGL selector text needed to grab all metal atoms in a site."""

        return " or ".join([
         metal.ngl_sele for metal in self.metal_set.all()
        ])


    @property
    def ngl_residues_sele(self):
        """The NGL selector text needed to grab all binding residues in a
        site."""

        return " or ".join([
         res.ngl_side_chain_sele for res in self.residue_set.all()
        ])


    @staticmethod
    def property_counts(sites, property, cutoff=None, unique=False):
        """Takes a series of sites and a property name, and returns a sort of
        histogram of the different values."""

        if unique: sites = sites.filter(representative=True)
        counts = Counter([str(site.__dict__[property]).upper() for site in sites]).most_common()
        if cutoff:
            counts = counts[:cutoff] + [
             ["OTHER", sum(n[1] for n in counts[cutoff:])]
            ]
        return [list(l) for l in zip(*counts)]


    @property
    def coordination(self):
        """Returns the number of liganding atoms in the site."""

        return [m.coordination for m in self.metal_set.all()]



class ChainCluster(models.Model):
    """A collection of chains with similar sequence."""

    class Meta:
        db_table = "chain_clusters"



class Chain(models.Model):
    """A chain of residues in a PDB."""

    class Meta:
        db_table = "chains"
        ordering = ["id"]

    id = models.CharField(primary_key=True, max_length=128)
    chain_pdb_identifier = models.CharField(max_length=128)
    sequence = models.TextField()
    spacers = models.CharField(max_length=128, blank=True, null=True)
    pdb = models.ForeignKey(Pdb, on_delete=models.CASCADE)
    cluster = models.ForeignKey(
     ChainCluster, on_delete=models.SET_NULL, null=True, blank=True
    )


    @staticmethod
    def create_from_atomium(chain, pdb, sequence):
        """Creates a chain record from an atomium Chain object and an existing
        Pdb record."""

        from .utilities import get_spacers
        return Chain.objects.create(
         id=f"{pdb.id}{chain.id}", pdb=pdb, spacers=get_spacers(sequence),
         sequence=sequence, chain_pdb_identifier=chain.id
        )


    @staticmethod
    def blast_search(sequence, elimit):
        """BLAST searches the PDB chains using a sequence. There must be a
        blastp program in the PATH for this to work."""

        p = subprocess.Popen(
         'echo "{}" | blastp -db data/chains.fasta -outfmt 15 -evalue {}'.format(sequence, elimit),
         stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )
        out, err = p.communicate()
        results = json.loads(out
         )["BlastOutput2"][0]["report"]["results"]["search"]["hits"]
        ids = [int(r["description"][0]["title"].split("|")[1]) for r in results]
        chains = sorted(
         Chain.objects.filter(id__in=ids), key=lambda c: ids.index(c.id)
        )
        for chain, result in zip(chains, results):
            chain.blast_data = result["hsps"][0]
        return chains


    @property
    def zincsites(self):
        """Returns all the ZincSite objects that have residues in this chain."""

        return set([csi.site for csi in ChainSiteInteraction.objects.filter(chain=self)])



class ChainSiteInteraction(models.Model):

    class Meta:
        db_table = "chain_site_interactions"

    chain = models.ForeignKey(Chain, on_delete=models.CASCADE, blank=True, null=True)
    site = models.ForeignKey(ZincSite, on_delete=models.CASCADE, blank=True, null=True)
    sequence = models.TextField()
    spacers = models.CharField(max_length=128, blank=True, null=True)



class Metal(models.Model):
    """A metal atom - usually zinc."""

    class Meta:
        db_table = "metals"

    atom_pdb_identifier = models.IntegerField()
    name = models.CharField(max_length=32)
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    element = models.CharField(max_length=8)
    residue_name = models.CharField(max_length=32)
    residue_pdb_identifier = models.IntegerField()
    insertion_pdb_identifier = models.CharField(max_length=128)
    chain_pdb_identifier = models.CharField(max_length=128)
    omission = models.TextField(blank=True, null=True)
    pdb = models.ForeignKey(Pdb, on_delete=models.CASCADE)
    site = models.ForeignKey(ZincSite, on_delete=models.CASCADE, blank=True, null=True)


    @staticmethod
    def create_from_atomium(atom, pdb, site=None, omission=None):
        """Creates a Metal record from an atomium atom."""

        residue = atom.structure
        numeric_id, insertion = residue.id.split(".")[1], ""
        while not numeric_id[-1].isdigit():
            insertion += numeric_id[-1]
            numeric_id = numeric_id[:-1]
        numeric_id = int(numeric_id)
        return Metal.objects.create(
         atom_pdb_identifier=atom.id, element=atom.element,
         name=atom.name, x=atom.x, y=atom.y, z=atom.z,
         residue_pdb_identifier=numeric_id, insertion_pdb_identifier=insertion,
         chain_pdb_identifier=atom.chain.id, residue_name=residue.name,
         pdb=pdb, omission=omission, site=site
        )


    @property
    def ngl_sele(self):
        """The NGL selector text needed to select the metal."""

        return (f"{self.residue_pdb_identifier}^" +
        f"{self.insertion_pdb_identifier}:{self.chain_pdb_identifier}/0 and .{self.name} and (%A or %)")


    @property
    def atomium_id(self):
        """Recreates the atomium ID of the residue."""

        return (f"{self.chain_pdb_identifier}:" +
        f"{self.residue_pdb_identifier}{self.insertion_pdb_identifier}")


    @property
    def coordination(self):
        return len(self.coordinatebond_set.all())



class Residue(models.Model):
    "A collection of atoms, usually in a row on a chain."

    class Meta:
        db_table = "residues"
        ordering = ["residue_pdb_identifier"]

    residue_pdb_identifier = models.IntegerField()
    insertion_pdb_identifier = models.CharField(max_length=128)
    name = models.CharField(max_length=128)
    atomium = models.CharField(max_length=128)
    chain_pdb_identifier = models.CharField(max_length=128)
    chain_signature = models.CharField(max_length=128, blank=True)
    site = models.ForeignKey(ZincSite, on_delete=models.CASCADE)
    chain = models.ForeignKey(Chain, blank=True, null=True, on_delete=models.CASCADE)


    @staticmethod
    def create_from_atomium(residue, chain, site, atom_dict):
        """Creates a residue record from an atomium Residue object and existing
        ZincSite and Chain records. You must specify the residue number."""

        numeric_id, insertion = residue.id.split(".")[1], ""
        while not numeric_id[-1].isdigit():
            insertion += numeric_id[-1]
            numeric_id = numeric_id[:-1]
        numeric_id = int(numeric_id)
        signature = []
        if residue.__class__.__name__ == "Residue":
            if residue.previous: signature = [residue.previous.name.lower()]
            signature.append(residue.name)
            if residue.next: signature.append(residue.next.name.lower())
        signature = ".".join(signature)
        residue_record = Residue.objects.create(
         residue_pdb_identifier=numeric_id, chain_pdb_identifier=residue.chain.id,
         insertion_pdb_identifier=insertion, chain_signature=signature,
         name=residue.name, chain=chain, site=site, atomium=residue.id
        )
        for atom in residue.atoms():
            atom_dict[atom.id] = Atom.create_from_atomium(atom, residue_record)
        return residue_record


    @property
    def ngl_sele(self):
        """The NGL selector text needed to select the residue."""

        return (f"{self.residue_pdb_identifier}^" +
        f"{self.insertion_pdb_identifier}:{self.chain_pdb_identifier}/0 and (%A or %)")


    @property
    def ngl_side_chain_sele(self):
        """The NGL selector text needed to select the residue side chain."""

        if self.name not in CODES or self.name in "ACTGU":
            return self.ngl_sele
        ligand_names = [a.name for a in self.atom_set.exclude(coordinatebond=None)]
        includes = ["sidechain", ".CA"]
        if "O" in ligand_names:
            includes += [".O", ".C"]
        if "N" in ligand_names:
            includes += [".N"]
        includes = " or ".join(includes)
        return f"({includes}) and {self.ngl_sele}"


    @staticmethod
    def name_counts(cutoff=None):
        """Returns the number of residues of each name in the database."""

        names = Residue.objects.filter(site__representative=True).values_list("name")
        counts = [[n[0], c] for n, c in Counter(names).most_common()]
        if cutoff:
            counts = counts[:cutoff] + [
             ["OTHER", sum(n[1] for n in counts[cutoff:])]
            ]
        return [list(l) for l in zip(*counts)]



class Atom(models.Model):
    """An atom in a liganding residue."""

    class Meta:
        db_table = "atoms"

    atom_pdb_identifier = models.IntegerField()
    name = models.CharField(max_length=32)
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    element = models.CharField(max_length=8)
    residue = models.ForeignKey(Residue, on_delete=models.CASCADE)


    @staticmethod
    def create_from_atomium(atom, residue):
        return Atom.objects.create(
         atom_pdb_identifier=atom.id,
         name=atom.name, x=atom.x, y=atom.y, z=atom.z,
         element=atom.element, residue=residue
        )


    @property
    def ngl_sele(self):
        """The NGL selector text needed to select the atom."""

        return (f"{self.residue.residue_pdb_identifier}^" +
        f"{self.residue.insertion_pdb_identifier}:{self.residue.chain_pdb_identifier}/0 and .{self.name}")



class CoordinateBond(models.Model):

    class Meta:
        db_table = "bonds"

    metal = models.ForeignKey(Metal, on_delete=models.CASCADE)
    atom = models.ForeignKey(Atom, on_delete=models.CASCADE)

    @property
    def ngl_sele(self):
        return f"['({self.metal.ngl_sele})', '({self.atom.ngl_sele})']"
