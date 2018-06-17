from collections import Counter
from django.shortcuts import render
from django.db.models import F
from zinc.models import ZincSite, Pdb, Residue

def home(request):
    """Returns the home page, along with some object counts."""

    return render(request, "home.html", {"counts": [
     len(set(ZincSite.objects.values_list("cluster", flat=True))),
     ZincSite.objects.count(),
     Pdb.objects.count()
    ]})


def changelog(request):
    """Returns the changelog page."""

    return render(request, "changelog.html")


def about(request):
    """Returns the about page."""

    return render(request, "about.html")


def data(request):
    residues = Residue.objects.exclude(site=None)
    residue_counts = Counter([res.name for res in residues]).most_common()
    residue_counts = residue_counts[:5] + [["Other", sum(n[1] for n in residue_counts[5:])]]
    residue_counts = [list(l) for l in zip(*residue_counts)]
    sites = ZincSite.objects.all().annotate(organism=F("pdb__organism"), classification=F("pdb__classification"), technique=F("pdb__technique"))
    species_counts = Counter([site.organism for site in sites]).most_common()
    species_counts = species_counts[:6] + [["Other", sum(n[1] for n in species_counts[6:])]]
    species_counts = [list(l) for l in zip(*species_counts)]
    class_counts = Counter([site.classification for site in sites]).most_common()
    class_counts = class_counts[:6] + [["Other", sum(n[1] for n in class_counts[6:])]]
    class_counts = [list(l) for l in zip(*class_counts)]
    technique_counts = Counter([site.technique for site in sites]).most_common()
    technique_counts = technique_counts[:3] + [["Other", sum(n[1] for n in technique_counts[3:])]]
    technique_counts = [list(l) for l in zip(*technique_counts)]
    return render(request, "data.html", {
     "bar_data": [residue_counts, technique_counts, species_counts, class_counts]
    })
