from django.shortcuts import render
from zinc.models import ZincSite, Pdb

def home(request):
    return render(request, "home.html", {"counts": [
     len(set(ZincSite.objects.values_list("cluster", flat=True))),
     ZincSite.objects.count(),
     Pdb.objects.count()
    ]})
