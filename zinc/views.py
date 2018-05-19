from django.shortcuts import render, redirect, get_object_or_404
from zinc.models import Pdb

def search(request):
    results = Pdb.search(request.GET["q"])
    return render(request, "search.html", {"results": results})


def pdb(request, code):
    pdb = get_object_or_404(Pdb, id=code)
    return render(request, "pdb.html", {"pdb": pdb})
