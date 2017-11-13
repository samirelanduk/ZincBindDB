"""ZincBind views."""

from django.shortcuts import render, redirect
from django.core.paginator import Paginator
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
    if "term" in request.GET:
        sites = omni_search(request.GET["term"])
        results = Paginator(sites, 25)
        page_number = request.GET.get("page", 1)
        try:
            page_number = int(page_number)
        except: page_number = 1
        if not 0 < page_number <= results.num_pages:
            page_number = 1
        page = results.page(page_number)
        return render(request, "search.html", {
         "term": request.GET["term"],
         "page_count": results.num_pages,
         "result_count": results.count,
         "results": page.object_list,
         "page": page.number,
         "previous": page.previous_page_number() if page.has_previous() else False,
         "next": page.next_page_number() if page.has_next() else False,
        })
    return redirect("/")



def site(request, site_id):
    site = ZincSite.objects.get(pk=site_id)
    return render(request, "site.html", {"site": site})
