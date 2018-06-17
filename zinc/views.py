from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.http import Http404
from zinc.models import Pdb, ZincSite

def search(request):
    results = []
    if request.GET:
        try:
            results = Pdb.search(request.GET["q"])
        except KeyError:
            try:
                results = Pdb.blast_search(request.GET["sequence"])
            except KeyError:
                results = Pdb.advanced_search(request.GET)
    else:
        return render(request, "advanced-search.html")
    paginated_results = Paginator(results, 25)
    try:
        page = paginated_results.page(request.GET.get("page", 1))
    except: raise Http404
    return render(request, "search-results.html", {
     "page": page, "results": paginated_results, "chains": "sequence" in request.GET
    })



def pdb(request, code):
    """Returns a particular Pdb's page."""
    
    pdb = get_object_or_404(Pdb, id=code)
    return render(request, "pdb.html", {"pdb": pdb})


def zinc_site(request, pk):
    """Returns a particular ZincSite's page."""

    site = get_object_or_404(ZincSite, id=pk)
    return render(request, "zinc-site.html", {"site": site})
