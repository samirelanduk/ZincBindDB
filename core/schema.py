import re
import graphene
from graphene_django.types import DjangoObjectType
from graphene.relay import Connection, ConnectionField
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



class CoordinateBondContainer:

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



class AtomType(CoordinateBondContainer, DjangoObjectType):

    class Meta:
        model = Atom



class AtomConnection(Connection):
    
    class Meta:
        node = AtomType
    
    count = graphene.Int()

    def resolve_count(self, info, **kwargs):
        return len(self.edges)



class AtomContainer:

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



class ResidueType(AtomContainer, DjangoObjectType):

    class Meta:
        model = Residue



class ResidueConnection(Connection):
    
    class Meta:
        node = ResidueType
    
    count = graphene.Int()

    def resolve_count(self, info, **kwargs):
        return len(self.edges)



class ResidueContainer:

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



class MetalType(CoordinateBondContainer, DjangoObjectType):

    class Meta:
        model = Metal



class MetalConnection(Connection):
    
    class Meta:
        node = MetalType
    
    count = graphene.Int()

    def resolve_count(self, info, **kwargs):
        return len(self.edges)



class MetalContainer:

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



class ZincSiteType(MetalContainer, ResidueContainer, DjangoObjectType):

    class Meta:
        model = ZincSite



class ZincSiteConnection(Connection):
    
    class Meta:
        node = ZincSiteType
    
    count = graphene.Int()

    def resolve_count(self, info, **kwargs):
        return len(self.edges)



class ZincSiteContainer:

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



class GroupType(ZincSiteContainer, DjangoObjectType):

    class Meta:
        model = Group



class GroupConnection(Connection):
    
    class Meta:
        node = GroupType
    
    count = graphene.Int()

    def resolve_count(self, info, **kwargs):
        return len(self.edges)



class GroupContainer:

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



class PdbType(ZincSiteContainer, MetalContainer, DjangoObjectType):

    class Meta:
        model = Pdb



class PdbConnection(Connection):
    
    class Meta:
        node = PdbType
    
    count = graphene.Int()

    def resolve_count(self, info, **kwargs):
        return len(self.edges)



class Query(ZincSiteContainer, MetalContainer, ResidueContainer, AtomContainer, CoordinateBondContainer, GroupContainer, graphene.ObjectType):
   
    version = graphene.String()
    pdb = graphene.Field(PdbType, id=graphene.String(required=True))
    pdbs = graphene.ConnectionField(PdbConnection, **generate_args(Pdb))
    

    def resolve_version(self, info, **kwargs):
        return "1.0.0"
    

    def resolve_pdb(self, info, **kwargs):
        try:
            return self.pdb_set.get(id=kwargs["id"])
        except AttributeError:
            return Pdb.objects.get(id=kwargs["id"])
    

    def resolve_pdbs(self, info, **kwargs):
        pdbs = Pdb.objects.filter(**process_kwargs(kwargs))
        if "sort" in kwargs: pdbs = pdbs.order_by(kwargs["sort"])
        return pdbs
    

schema = graphene.Schema(query=Query)

