from collections import Counter
from django.shortcuts import render
from django.db.models import F
from django.http import HttpResponse
from django.core.management import call_command
from zinc.models import ZincSite, Pdb, Residue, ZincSiteCluster
from zinc.views import search

def home(request):
    """Returns the home page, along with some object counts."""

    return render(request, "home.html", {"counts": [
     ZincSiteCluster.objects.count(),
     ZincSite.objects.count(),
     Pdb.objects.count()
    ]})


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
     technique=F("pdb__technique")
    )
    technique_counts = ZincSite.property_counts(sites, "technique", 3)
    species_counts = ZincSite.property_counts(sites, "organism", 6)
    class_counts = ZincSite.property_counts(sites, "classification", 6)
    code_counts = ZincSite.property_counts(sites, "code", 9)
    print(code_counts)
    return render(request, "data.html", {
     "bar_data": [residue_counts, technique_counts, species_counts, class_counts, code_counts]
    })


def all_data(request):
    request.GET = request.GET.copy()
    request.GET["q"] = " "
    return search(request)
