"""ZincBind views."""

from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from .models import ZincSite, Pdb
from .search import omni_search, specific_search

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
    if not request.GET:
        return advanced_search(request)
    else:
        return process_search(request)


def advanced_search(request):
    return render(request, "advanced-search.html")


def process_search(request):
    if "term" in request.GET:
        sites = omni_search(
         "" if request.GET["term"] == "*" else request.GET["term"]
        )
    else:
        sites = specific_search(**request.GET)
    results = Paginator(sites, 25)
    page_number = request.GET.get("page", 1)
    try:
        page_number = int(page_number)
    except: page_number = 1
    if not 0 < page_number <= results.num_pages:
        page_number = 1
    page = results.page(page_number)
    url = "/search?"
    if "term" in request.GET:
        url += "term=" + request.GET["term"]
    else:
        url +=  "&".join(["{}={}".format(
         term, request.GET[term].replace(" " , "+")
        ) for term in request.GET if term != "page"])
    return render(request, "search.html", {
     "term": request.GET.get("term"),
     "page_count": results.num_pages,
     "result_count": results.count,
     "results": page.object_list,
     "page": page.number,
     "previous": page.previous_page_number() if page.has_previous() else False,
     "next": page.next_page_number() if page.has_next() else False,
     "url": url
    })


def site(request, site_id):
    try:
        site = ZincSite.objects.get(pk=site_id)
        pdb_sites = ZincSite.objects.filter(pdb=site.pdb).exclude(id=site.id)
        species_sites = ZincSite.objects.filter(pdb__organism__contains=site.pdb.organism).exclude(id=site.id)
        return render(request, "site.html", {
         "site": site, "pdb_sites": pdb_sites, "species_sites": species_sites
        })
    except ObjectDoesNotExist:
        raise Http404


def ngl_site(request, site_id):
    try:
        site = ZincSite.objects.get(pk=site_id)
        return render(request, "ngl-site.html", {"site": site})
    except ObjectDoesNotExist:
        raise Http404


def changelog(request):
    return render(request, "changelog.html")
