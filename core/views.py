from collections import Counter
from django.shortcuts import render
from django.db.models import F
from zinc.models import ZincSite, Pdb, Residue, ZincSiteCluster

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

    residue_counts = Residue.name_counts(5)
    sites = ZincSite.objects.all().annotate(
     organism=F("pdb__organism"),
     classification=F("pdb__classification"),
     technique=F("pdb__technique")
    )
    technique_counts = ZincSite.property_counts(sites, "technique", 3)
    species_counts = ZincSite.property_counts(sites, "organism", 6)
    class_counts = ZincSite.property_counts(sites, "classification", 6)
    return render(request, "data.html", {
     "bar_data": [residue_counts, technique_counts, species_counts, class_counts]
    })
