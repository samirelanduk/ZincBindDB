from django.shortcuts import render, redirect, get_object_or_404
from zinc.models import Pdb

def pdb(request, code):
    pdb = get_object_or_404(Pdb, id=code)
    return render(request, "pdb.html", {"pdb": pdb})
