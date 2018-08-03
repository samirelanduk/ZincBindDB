from rest_framework import mixins
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework import viewsets
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.http import Http404, JsonResponse
from zinc.models import *
from zinc.serializers import *

def search(request):
    """The search view - it returns the advanced search page if no query is sent
    and otherwise uses the query to search the database. The exact search
    function used depends on the exact query sent."""

    results = []
    if request.GET:
        try:
            results = Pdb.search(request.GET["q"])
        except KeyError:
            if "sequence" in request.GET:
                try:
                    results = Pdb.blast_search(request.GET["sequence"])
                except: results = []
            else:
                results = Pdb.advanced_search(request.GET)
    else:
        return render(request, "advanced-search.html")
    paginated_results = Paginator(results, 25)
    try:
        page = paginated_results.page(request.GET.get("page", 1))
    except: raise Http404
    return render(request, "search-results.html", {
     "page": page, "results": paginated_results,
     "chains": "sequence" in request.GET
    })



def pdb(request, code):
    """Returns a particular Pdb"s page."""

    pdb = get_object_or_404(Pdb, id=code)
    return render(request, "pdb.html", {"pdb": pdb})


def zinc_site(request, pk):
    """Returns a particular ZincSite"s page."""

    site = get_object_or_404(ZincSite, id=pk)
    return render(request, "zinc-site.html", {"site": site})


def api(request):
    return render(request, "api.html")


@api_view(["GET"])
def api_object(request, type, pk):
    lookup = {
     "pdbs": PdbSerializer,
     "sites": ZincSiteSerializer,
     "metals": MetalSerializer,
     "residues": ResidueSerializer,
     "atoms": AtomSerializer,
     "chains": ChainSerializer,
     "chain-clusters": ChainClusterSerializer,
     "site-clusters": ZincSiteClusterSerializer,
    }
    obj = get_object_or_404(lookup[type].Meta.model, id=pk)
    return Response(lookup[type](obj).data)



class PdbViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Pdb.objects.all()
    serializer_class = PdbSerializer



class ZincSiteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ZincSite.objects.all()
    serializer_class = ZincSiteSerializer



class ZincSiteClusterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ZincSiteCluster.objects.all()
    serializer_class = ZincSiteClusterSerializer


class ChainClusterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ChainCluster.objects.all()
    serializer_class = ChainClusterSerializer
