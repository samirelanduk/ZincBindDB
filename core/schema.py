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
        if key != "sort":
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
        if field_type == "CharField":
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
    args["sort"] = graphene.String()
    return args



class PdbType(DjangoObjectType):

    class Meta:
        model = Pdb



class PdbConnection(Connection):
    
    class Meta:
        node = PdbType
    
    count = graphene.Int()

    def resolve_count(self, info, **kwargs):
        return len(self.edges)



class Query(graphene.ObjectType):
   
    version = graphene.String()
    pdb = graphene.Field(PdbType, id=graphene.String(required=True))
    pdbs = graphene.ConnectionField(PdbConnection, **generate_args(Pdb))

    def resolve_version(self, info, **kwargs):
        return "1.0.0"
    

    def resolve_pdb(self, info, **kwargs):
        return Pdb.objects.get(id=kwargs["id"])
    

    def resolve_pdbs(self, info, **kwargs):
        pdbs = Pdb.objects.filter(**process_kwargs(kwargs))
        if "sort" in kwargs: pdbs = pdbs.order_by(kwargs["sort"])
        return pdbs


schema = graphene.Schema(query=Query)

