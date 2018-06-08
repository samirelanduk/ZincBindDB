from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.http import Http404
from zinc.models import Pdb, ZincSite

def search(request):
    if request.GET:
        try:
            results = Pdb.search(request.GET["q"])
        except:
            results = Pdb.advanced_search(request.GET)
        paginated_results = Paginator(results, 25)
        try:
            page = paginated_results.page(request.GET.get("page", 1))
        except: raise Http404
        return render(request, "search-results.html", {
         "page": page, "results": paginated_results
        })
    return render(request, "advanced-search.html")


def pdb(request, code):
    pdb = get_object_or_404(Pdb, id=code)
    return render(request, "pdb.html", {"pdb": pdb})


def zinc_site(request, pk):
    site = get_object_or_404(ZincSite, id=pk)
    return render(request, "zinc-site.html", {"site": site})
