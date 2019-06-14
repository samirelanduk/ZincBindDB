from graphene_django.views import GraphQLView
from django.urls import path

urlpatterns = [
 path("", GraphQLView.as_view(graphiql=True)),
]
