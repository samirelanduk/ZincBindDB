from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url="/", redirect_field_name=None)
def new_site_page(request):
    if request.method == "POST":
        return redirect(
         "/sites/{}{}/".format(request.POST["pdb"], request.POST["zinc"])
        )
    return render(request, "new-site.html")


def site_page(request, site_id):
    return render(request, "site.html")
