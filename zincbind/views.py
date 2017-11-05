"""ZincBind views."""

from django.shortcuts import render
from .models import ZincSite, Pdb

def home(request):
    return render(request, "home.html", {
     "zinc_count": ZincSite.objects.count(),
     "pdb_count": Pdb.objects.exclude(title=None).count()
    })
