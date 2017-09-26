from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib.auth.decorators import login_required
from zincsites.models import ZincSite

# Create your views here.
@login_required(login_url="/", redirect_field_name=None)
def new_site_page(request):
    if request.method == "POST":
        residues = list(filter(bool, [
         request.POST[key] for key in request.POST if key.startswith("residue")
        ]))
        create_site(request.POST["pdb"], request.POST["zinc"], residues)
        return redirect(
         "/sites/{}{}/".format(request.POST["pdb"], request.POST["zinc"])
        )
    return render(request, "new-site.html")


def site_page(request, site_id):
    try:
        site = ZincSite.objects.get(pk=site_id)
    except: raise Http404
    return render(request, "site.html", {"site": site})


def create_site(pdb, zinc, residues):
    zinc_id = pdb + zinc
    ZincSite.objects.create(id=zinc_id)
