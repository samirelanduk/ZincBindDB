import atomium
from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib.auth.decorators import login_required
from zincsites.models import ZincSite, Pdb, Residue
from zincsites.exceptions import InvalidPdbError

# Create your views here.
@login_required(login_url="/", redirect_field_name=None)
def new_site_page(request):
    if request.method == "POST":
        residues = list(filter(bool, [
         request.POST[key] for key in request.POST if key.startswith("residue")
        ]))
        try:
            create_site(request.POST["pdb"], request.POST["zinc"], residues)
        except InvalidPdbError:
            return render(request, "new-site.html", {
             "error_message": "{} is an invalid PDB".format(request.POST["pdb"])
            })
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
    pdb = create_pdb(pdb)
    residues = [create_residue(res, pdb) for res in residues]
    site = ZincSite.objects.create(id=zinc_id)
    for residue in residues:
        site.residues.add(residue)
    return site


def create_pdb(code):
    try:
        data = atomium.fetch_data(code, pdbe=True)
        if data is None: raise InvalidPdbError
    except Exception as e:
        raise InvalidPdbError
    try:
        Pdb.objects.create(
         id=code, deposition_date=data["deposition_date"], title=data["title"]
        )
    except: pass
    return data


def create_residue(residue_id, pdb_data):
    pdb = Pdb.objects.get(id=pdb_data["code"])
    for model in pdb_data["models"]:
        for chain in model["chains"]:
            for residue in chain["residues"]:
                if residue["id"] == residue_id:
                    number = int("".join(char for char in residue_id if char.isdigit()))
                    return Residue.objects.create(
                     id=residue["id"], chain=chain["chain_id"], number=number,
                     name=residue["name"], pdb=pdb
                    )
