import re
import graphene
from graphene_django.types import DjangoObjectType
from graphene.relay import Connection, ConnectionField
from django.conf import settings
from .models import *

def camel_case(string, suffix=None):
    """Converts a string in snake_case to a string in camelCase. If a suffix is
    given, this will be added to the end after a double underscore.

    title becomes title, deposition_date becomes depositionDate, with a suffix
    it would be depositionDate__suffix."""

    string =  "".join([
     x.title() if n > 0 else x for n, x in enumerate(string.split("_"))
    ])
    if suffix: string += f"__{suffix}"
    return string


def process_kwargs(kwargs):
    """Takes some arguments sent in from a GraphQL query, removes those which
    can't be passed to a model filter, and converts any camelCase keys to
    snake_case."""

    processed = {}
    for key, value in kwargs.items():
        if key not in ["sort", "first", "last"]:
            key = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", key)
            key = re.sub("([a-z0-9])([A-Z])", r"\1_\2", key).lower()
            processed[key] = value
    return processed


def add_field_to_args(args, field, Type, suffixes):
    """Takes a django model field, and adds it to a dictionary representing the
    arguments that can be passed to a GraphQL field. Variants with different
    suffixes can be specified."""

    args[field.name] = Type()
    for suffix in suffixes:
        gql_field = Type(name=camel_case(field.name, suffix))
        args[camel_case(field.name, suffix)] = gql_field


def generate_args(Model):
    """Generates a dictionary representing the fields that can be passed to a
    GraphQL field, for a given model."""

    args = {}
    for field in Model._meta.get_fields(include_parents=False):
        field_type = field.get_internal_type()
        if field_type == "CharField" or field_type == "TextField":
            add_field_to_args(args, field, graphene.String, ("contains",))
        elif field_type == "FloatField":
            add_field_to_args(
             args, field, graphene.Float, ("lt", "gt", "lte", "gte")
            )
        elif field_type == "DateField":
            add_field_to_args(
             args, field, graphene.String, ("lt", "gt", "lte", "gte")
            )
        elif field_type == "IntegerField":
            add_field_to_args(
             args, field, graphene.Int, ("lt", "gt", "lte", "gte")
            )
        elif field_type == "BooleanField":
            add_field_to_args(
             args, field, graphene.Boolean, ()
            )
    args["sort"] = graphene.String()
    return args



class CoordinateBondType(DjangoObjectType):

    class Meta:
        model = CoordinateBond



class CoordinateBondConnection(Connection):
    
    class Meta:
        node = CoordinateBondType
    
    count = graphene.Int()

    def resolve_count(self, info, **kwargs):
        return len(self.edges)



class HasCoordinateBonds:

    coordinate_bond = graphene.Field(CoordinateBondType, id=graphene.Int(required=True))
    coordinate_bonds = graphene.ConnectionField(CoordinateBondConnection, **generate_args(CoordinateBond))

    def resolve_coordinate_bond(self, info, **kwargs):
        try:
            return self.coordinatebond_set.get(id=kwargs["id"])
        except AttributeError:
            return CoordinateBond.objects.get(id=kwargs["id"])
    

    def resolve_coordinate_bonds(self, info, **kwargs):
        try:
            coordinate_bonds = self.coordinatebond_set.filter(**process_kwargs(kwargs))
        except AttributeError:
            coordinate_bonds = CoordinateBond.objects.filter(**process_kwargs(kwargs))
        if "sort" in kwargs: coordinate_bonds = coordinate_bonds.order_by(kwargs["sort"])
        return coordinate_bonds



class AtomType(HasCoordinateBonds, DjangoObjectType):

    class Meta:
        model = Atom



class AtomConnection(Connection):
    
    class Meta:
        node = AtomType
    
    count = graphene.Int()

    def resolve_count(self, info, **kwargs):
        return len(self.edges)



class HasAtoms:

    atom = graphene.Field(AtomType, id=graphene.Int(required=True))
    atoms = graphene.ConnectionField(AtomConnection, **generate_args(Atom))

    def resolve_atom(self, info, **kwargs):
        try:
            return self.atom_set.get(id=kwargs["id"])
        except AttributeError:
            return Atom.objects.get(id=kwargs["id"])
    

    def resolve_atoms(self, info, **kwargs):
        try:
            atoms = self.atom_set.filter(**process_kwargs(kwargs))
        except AttributeError:
            atoms = Atom.objects.filter(**process_kwargs(kwargs))
        if "sort" in kwargs: atoms = atoms.order_by(kwargs["sort"])
        return atoms



class ResidueType(HasAtoms, DjangoObjectType):

    class Meta:
        model = Residue



class ResidueConnection(Connection):
    
    class Meta:
        node = ResidueType
    
    count = graphene.Int()

    def resolve_count(self, info, **kwargs):
        return len(self.edges)



class HasResidues:

    residue = graphene.Field(ResidueType, id=graphene.Int(required=True))
    residues = graphene.ConnectionField(ResidueConnection, **generate_args(Residue))

    def resolve_residue(self, info, **kwargs):
        try:
            return self.residue_set.get(id=kwargs["id"])
        except AttributeError:
            return Residue.objects.get(id=kwargs["id"])
    

    def resolve_residues(self, info, **kwargs):
        try:
            residues = self.residue_set.filter(**process_kwargs(kwargs))
        except AttributeError:
            residues = Residue.objects.filter(**process_kwargs(kwargs))
        if "sort" in kwargs: residues = residues.order_by(kwargs["sort"])
        return residues



class MetalType(HasCoordinateBonds, DjangoObjectType):

    class Meta:
        model = Metal



class MetalConnection(Connection):
    
    class Meta:
        node = MetalType
    
    count = graphene.Int()

    def resolve_count(self, info, **kwargs):
        return len(self.edges)



class HasMetals:

    metal = graphene.Field(MetalType, id=graphene.Int(required=True))
    metals = graphene.ConnectionField(MetalConnection, **generate_args(Metal))

    def resolve_metal(self, info, **kwargs):
        try:
            return self.metal_set.get(id=kwargs["id"])
        except AttributeError:
            return Metal.objects.get(id=kwargs["id"])
    

    def resolve_metals(self, info, **kwargs):
        try:
            metals = self.metal_set.filter(**process_kwargs(kwargs))
        except AttributeError:
            metals = Metal.objects.filter(**process_kwargs(kwargs))
        if "sort" in kwargs: metals = metals.order_by(kwargs["sort"])
        return metals



class ChainInteractionType(DjangoObjectType):

    class Meta:
        model = ChainInteraction



class ChainInteractionConnection(Connection):
    
    class Meta:
        node = ChainInteractionType
    
    count = graphene.Int()

    def resolve_count(self, info, **kwargs):
        return len(self.edges)



class HasChainInteractions:

    chain_interaction = graphene.Field(ChainInteractionType, id=graphene.Int(required=True))
    chain_interactions = graphene.ConnectionField(ChainInteractionConnection, **generate_args(ChainInteraction))

    def resolve_chain_interaction(self, info, **kwargs):
        try:
            return self.chaininteraction_set.get(id=kwargs["id"])
        except AttributeError:
            return ChainInteraction.objects.get(id=kwargs["id"])
    

    def resolve_chain_interactions(self, info, **kwargs):
        try:
            chaininteractions = self.chaininteraction_set.filter(**process_kwargs(kwargs))
        except AttributeError:
            chaininteractions = ChainInteraction.objects.filter(**process_kwargs(kwargs))
        if "sort" in kwargs: chaininteractions = chaininteractions.order_by(kwargs["sort"])
        return chaininteractions



class ZincSiteType(HasMetals, HasResidues, HasChainInteractions, DjangoObjectType):

    class Meta:
        model = ZincSite



class ZincSiteConnection(Connection):
    
    class Meta:
        node = ZincSiteType
    
    count = graphene.Int()

    def resolve_count(self, info, **kwargs):
        return len(self.edges)



class HasZincSites:

    zincsite = graphene.Field(ZincSiteType, id=graphene.String(required=True))
    zincsites = graphene.ConnectionField(ZincSiteConnection, **generate_args(ZincSite))

    def resolve_zincsite(self, info, **kwargs):
        try:
            return self.zincsite_set.get(id=kwargs["id"])
        except AttributeError:
            return ZincSite.objects.get(id=kwargs["id"])
    

    def resolve_zincsites(self, info, **kwargs):
        try:
            zincsites = self.zincsite_set.filter(**process_kwargs(kwargs))
        except AttributeError:
            zincsites = ZincSite.objects.filter(**process_kwargs(kwargs))
        if "sort" in kwargs: zincsites = zincsites.order_by(kwargs["sort"])
        return zincsites



class GroupType(HasZincSites, DjangoObjectType):

    class Meta:
        model = Group



class GroupConnection(Connection):
    
    class Meta:
        node = GroupType
    
    count = graphene.Int()

    def resolve_count(self, info, **kwargs):
        return len(self.edges)



class HasGroups:

    group = graphene.Field(GroupType, id=graphene.String(required=True))
    groups = graphene.ConnectionField(GroupConnection, **generate_args(Group))

    def resolve_group(self, info, **kwargs):
        try:
            return self.group_set.get(id=kwargs["id"])
        except AttributeError:
            return Group.objects.get(id=kwargs["id"])
    

    def resolve_groups(self, info, **kwargs):
        try:
            groups = self.group_set.filter(**process_kwargs(kwargs))
        except AttributeError:
            groups = Group.objects.filter(**process_kwargs(kwargs))
        if "sort" in kwargs: groups = groups.order_by(kwargs["sort"])
        return groups



class ChainType(HasResidues, HasChainInteractions, DjangoObjectType):

    class Meta:
        model = Chain



class ChainConnection(Connection):
    
    class Meta:
        node = ChainType
    
    count = graphene.Int()

    def resolve_count(self, info, **kwargs):
        return len(self.edges)



class HasChains:

    chain = graphene.Field(ChainType, id=graphene.String(required=True))
    chains = graphene.ConnectionField(ChainConnection, **generate_args(Chain))

    def resolve_chain(self, info, **kwargs):
        try:
            return self.chain_set.get(id=kwargs["id"])
        except AttributeError:
            return Chain.objects.get(id=kwargs["id"])
    

    def resolve_chains(self, info, **kwargs):
        try:
            chains = self.chain_set.filter(**process_kwargs(kwargs))
        except AttributeError:
            chains = Chain.objects.filter(**process_kwargs(kwargs))
        if "sort" in kwargs: chains = chains.order_by(kwargs["sort"])
        return chains



class ChainClusterType(HasChains, DjangoObjectType):

    class Meta:
        model = ChainCluster



class ChainClusterConnection(Connection):
    
    class Meta:
        node = ChainClusterType
    
    count = graphene.Int()

    def resolve_count(self, info, **kwargs):
        return len(self.edges)



class HasChainClusters:

    chain_cluster = graphene.Field(ChainClusterType, id=graphene.String(required=True))
    chain_clusters = graphene.ConnectionField(ChainClusterConnection, **generate_args(ChainCluster))

    def resolve_chain_cluster(self, info, **kwargs):
        try:
            return self.chaincluster_set.get(id=kwargs["id"])
        except AttributeError:
            return ChainCluster.objects.get(id=kwargs["id"])
    

    def resolve_chain_clusters(self, info, **kwargs):
        try:
            chainclusters = self.chaincluster_set.filter(**process_kwargs(kwargs))
        except AttributeError:
            chainclusters = ChainCluster.objects.filter(**process_kwargs(kwargs))
        if "sort" in kwargs: chainclusters = chainclusters.order_by(kwargs["sort"])
        return chainclusters



class PdbType(HasZincSites, HasMetals, HasChains, DjangoObjectType):

    class Meta:
        model = Pdb



class PdbConnection(Connection):
    
    class Meta:
        node = PdbType
    
    count = graphene.Int()

    def resolve_count(self, info, **kwargs):
        return len(self.edges)



class HasPdbs:

    pdb = graphene.Field(PdbType, id=graphene.String(required=True))
    pdbs = graphene.ConnectionField(PdbConnection, **generate_args(Pdb))

    def resolve_pdb(self, info, **kwargs):
        try:
            return self.pdb_set.get(id=kwargs["id"])
        except AttributeError:
            return Pdb.objects.get(id=kwargs["id"])
    

    def resolve_pdbs(self, info, **kwargs):
        pdbs = Pdb.objects.filter(**process_kwargs(kwargs))
        if "sort" in kwargs: pdbs = pdbs.order_by(kwargs["sort"])
        return pdbs
    


class BlastType(graphene.ObjectType):
    
    id = graphene.String()
    title = graphene.String()
    qseq = graphene.String()
    midline = graphene.String()
    hseq = graphene.String()
    bit_score = graphene.Float()
    evalue = graphene.Float()
    hit_from = graphene.Int()
    hit_to = graphene.Int()
    query_from = graphene.Int()
    query_to = graphene.Int()
    identity = graphene.Int()
    score = graphene.Int()
    chain = graphene.Field(ChainType)

    def resolve_chain(self, info, **kwargs):
        return Chain.objects.get(id=self["title"].split("|")[1])



class BlastConnection(Connection):
    
    class Meta:
        node = BlastType
    
    count = graphene.Int()

    def resolve_count(self, info, **kwargs):
        return len(self.edges)



class Query(HasPdbs, HasZincSites, HasMetals, HasResidues, HasAtoms, HasChains,
            HasCoordinateBonds, HasGroups, HasChainClusters,
            HasChainInteractions, graphene.ObjectType):
   
    version = graphene.String()
    blast = graphene.ConnectionField(
     BlastConnection, sequence=graphene.String(required=True),
     evalue=graphene.Float()
    )
    
    def resolve_version(self, info, **kwargs):
        return settings.VERSION
    

    def resolve_blast(self, info, **kwargs):
        results = Chain.blast_search(kwargs["sequence"], kwargs.get("evalue", 0.1))
        return results
    
    
schema = graphene.Schema(query=Query)

