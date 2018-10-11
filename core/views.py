from collections import Counter
from rest_framework import mixins
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework import viewsets
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F
from django.http import HttpResponse, Http404, JsonResponse
from django.core.management import call_command
from django.core.paginator import Paginator
from .models import *
from .serializers import *

def home(request):
    """Returns the home page, along with some object counts."""

    return render(request, "home.html", {"counts": [
     ZincSiteCluster.objects.count(),
     ZincSite.objects.count(),
     Pdb.objects.count()
    ]})


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
                    results = Pdb.blast_search(request.GET["sequence"], request.GET["threshold"])
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
    return render(request, "api.html", {
     "metal": Metal.objects.last(),
     "residue": Residue.objects.last(),
     "atom": Atom.objects.last(),
     "chain_cluster": ChainCluster.objects.first(),
     "site_cluster": ZincSiteCluster.objects.first()
    })


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



class PdbSearchResults(viewsets.ReadOnlyModelViewSet):
    serializer_class = PdbSerializer

    def get_queryset(self):
        try:
            results = Pdb.search(self.request.GET["q"])
        except KeyError:
            results = Pdb.advanced_search(self.request.GET)
        return results



class ZincSiteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ZincSite.objects.all()
    serializer_class = ZincSiteSerializer



class ZincSiteClusterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ZincSiteCluster.objects.all()
    serializer_class = ZincSiteClusterSerializer


class ChainClusterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ChainCluster.objects.all()
    serializer_class = ChainClusterSerializer



def changelog(request):
    """Returns the changelog page."""

    return render(request, "changelog.html")


def about(request):
    """Returns the about page."""

    return render(request, "about.html")


def help(request):
    """Returns the help page."""

    return render(request, "help.html")


def data(request):
    """Returns the data page and the relevant values needed for its charts."""

    if request.method == "POST":
        with open(
         "data/zinc." + request.POST["datatype"],
         "r" + ("b" if request.POST["datatype"] == "sqlite3" else "")
        ) as f:
            filebody = f.read()
        response = HttpResponse(
         filebody, content_type="application/plain-text"
        )
        response["Content-Disposition"] = 'attachment; filename="zinc.{}"'.format(
         request.POST["datatype"]
        )
        return response
    residue_counts = Residue.name_counts(5)
    sites = ZincSite.objects.all().annotate(
     organism=F("pdb__organism"),
     classification=F("pdb__classification"),
     technique=F("pdb__technique"),
     resolution=F("pdb__resolution")
    )
    technique_counts = ZincSite.property_counts(sites, "technique", 3)
    species_counts = ZincSite.property_counts(sites, "organism", 6)
    class_counts = ZincSite.property_counts(sites, "classification", 6)
    code_counts = ZincSite.property_counts(sites, "code", 9, unique=True)
    resolutions = [["<1.5Å ", "1.5-2.0Å", "2.0-2.5Å", "2.5-3.0Å", "3.0Å+", "None"], [
     sites.filter(resolution__lt=1.5).count(),
     sites.filter(resolution__lt=2.0, resolution__gte=1.5).count(),
     sites.filter(resolution__lt=2.5, resolution__gte=2.0).count(),
     sites.filter(resolution__lt=3.0, resolution__gte=2.5).count(),
     sites.filter(resolution__gte=3.0).count(),
     sites.filter(resolution=None).count(),
    ]]
    return render(request, "data.html", {
     "bar_data": [residue_counts, technique_counts, species_counts, class_counts, code_counts, resolutions]
    })


def all_data(request):
    request.GET = request.GET.copy()
    request.GET["q"] = " "
    return search(request)
