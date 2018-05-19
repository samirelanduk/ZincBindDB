from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from zinc.models import Pdb

def search(request):
    results = Pdb.search(request.GET["q"])
    paginated_results = Paginator(results, 25)
    page = paginated_results.page(request.GET.get("page", 1))
    return render(request, "search.html", {
     "page": page, "results": paginated_results
    })


def pdb(request, code):
    pdb = get_object_or_404(Pdb, id=code)
    return render(request, "pdb.html", {"pdb": pdb})
