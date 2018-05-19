from django.shortcuts import render, redirect, get_object_or_404
from zinc.models import Pdb

def search(request):
    return render(request, "search.html")


def pdb(request, code):
    pdb = get_object_or_404(Pdb, id=code)
    return render(request, "pdb.html", {"pdb": pdb})
