import graphene
from graphene_django.types import DjangoObjectType
from graphene.relay import Connection, ConnectionField

class Query(graphene.ObjectType):
   
    version = graphene.String()

    def resolve_version(self, info, **kwargs):
        return "1.0.0"


schema = graphene.Schema(query=Query)