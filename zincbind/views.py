"""ZincBind views."""

from collections import Counter
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from .models import ZincSite, Pdb, Residue
from .search import omni_search, specific_search

def home(request):
    return render(request, "home.html", {
     "zinc_count": ZincSite.objects.count(),
     "pdb_count": Pdb.objects.exclude(title=None).count()
    })


def data(request):
    valid = Pdb.objects.exclude(title=None)
    residue_frequencies = Counter(Residue.objects.values_list("name", flat=True))
    common_residues = residue_frequencies.most_common(7)
    residue_frequencies = common_residues + [
     ("Other", sum(
      residue_frequencies.values()) - sum([l[1] for l in common_residues]
     ))
    ]
    species_frequencies = Counter(
     ZincSite.objects.values_list("pdb__organism", flat=True)
    )
    common_species = species_frequencies.most_common(7)
    species_frequencies = common_species + [
     ("Other", sum(
      species_frequencies.values()) - sum([l[1] for l in common_species]
     ))
    ]
    class_frequencies = Counter(
     ZincSite.objects.values_list("pdb__classification", flat=True)
    )
    common_classes = class_frequencies.most_common(7)
    class_frequencies = common_classes + [
     ("Other", sum(
      class_frequencies.values()) - sum([l[1] for l in common_classes]
     ))
    ]
    return render(request, "data.html", {
     "pdb_with_zinc": valid.count(),
     "pdb_without_zinc": Pdb.objects.filter(title=None).count(),
     "residue_frequencies": [list(l) for l in list(zip(*residue_frequencies))],
     "species_frequencies": [list(l) for l in list(zip(*species_frequencies))],
     "class_frequencies": [list(l) for l in list(zip(*class_frequencies))]
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
        class_sites = ZincSite.objects.filter(
         pdb__classification=site.pdb.classification
        ).exclude(id=site.id).order_by("-pdb__deposited")
        if not site.pdb.classification:
            class_sites = ZincSite.objects.filter(id="XXXXXXXXX")
        return render(request, "site.html", {
         "site": site, "pdb_sites": pdb_sites, "class_sites": class_sites
        })
    except ObjectDoesNotExist:
        raise Http404


def changelog(request):
    return render(request, "changelog.html")
