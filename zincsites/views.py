import atomium
import django.shortcuts as shortcuts
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from zincsites.models import ZincSite, Pdb, Residue
from zincsites.factories import create_manual_zinc_site, update_zinc_residues
from zincsites.exceptions import *

# Create your views here.
@login_required(login_url="/", redirect_field_name=None)
def new_site_page(request):
    if request.method == "POST":
        if not request.POST["pdb"]:
            return shortcuts.render(request, "new-site.html", {
             "error": "No PDB code supplied"
            })
        if not request.POST["zinc"]:
            return shortcuts.render(request, "new-site.html", {
             "error": "No Zinc ID supplied"
            })
        residues = list(filter(bool, [
         request.POST[key] for key in request.POST if key.startswith("residue")
        ]))
        if not residues:
            return shortcuts.render(request, "new-site.html", {
             "error": "No Residue IDs supplied"
            })
        try:
            create_manual_zinc_site(
             request.POST["pdb"], request.POST["zinc"], residues
            )
        except InvalidPdbError:
            return shortcuts.render(request, "new-site.html", {
             "error": "'{}' is not a valid PDB".format(request.POST["pdb"])
            })
        except DuplicateSiteError:
            return shortcuts.render(request, "new-site.html", {
             "error": "There is already a zinc site called '{}'".format(
              request.POST["pdb"] + request.POST["zinc"]
             )
            })
        except NoSuchZincError:
            return shortcuts.render(request, "new-site.html", {
             "error": "There is no Zinc with ID '{}' in {}".format(
              request.POST["zinc"], request.POST["pdb"]
             )
            })
        except NoSuchResidueError as e:
            return shortcuts.render(request, "new-site.html", {
             "error": "There is no Residue with ID '{}' in {}".format(
              str(e), request.POST["pdb"]
             )
            })
        return shortcuts.redirect(
         "/sites/{}{}/".format(request.POST["pdb"], request.POST["zinc"])
        )
    return shortcuts.render(request, "new-site.html")


def site_page(request, site_id):
    try:
        site = ZincSite.objects.get(pk=site_id)
    except ObjectDoesNotExist: raise Http404
    return shortcuts.render(request, "site.html", {"site": site})


def sites_page(request):
    sites = ZincSite.objects.all()
    return shortcuts.render(request, "sites.html", {"sites": sites})


@login_required(login_url="/", redirect_field_name=None)
def edit_site_page(request, site_id):
    try:
        site = ZincSite.objects.get(pk=site_id)
    except ObjectDoesNotExist: raise Http404
    if request.method == "POST":
        residues = list(filter(bool, [
         request.POST[key] for key in request.POST if key.startswith("residue")
        ]))
        update_zinc_residues(residues, site)
        return shortcuts.redirect("/sites/{}/".format(site_id))
    return shortcuts.render(request, "edit-site.html", {"site": site})
