"""ZincBind views."""

from django.shortcuts import render
from .models import ZincSite, Pdb
from .search import omni_search

def home(request):
    return render(request, "home.html", {
     "zinc_count": ZincSite.objects.count(),
     "pdb_count": Pdb.objects.exclude(title=None).count()
    })


def data(request):
    valid = Pdb.objects.exclude(title=None)
    return render(request, "data.html", {
     "pdb_with_zinc": valid.count(),
     "pdb_without_zinc": Pdb.objects.filter(title=None).count(),
    })


def search(request):
    if request.method == "POST":
        return render(request, "search.html", {
         "term": request.POST["term"],
         "results": omni_search(request.POST["term"])
        })



def site(request, site_id):
    return render(request, "site.html")
