from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

def home_page(request):
    return render(request, "home.html")


def about_page(request):
    return render(request, "about.html")


def help_page(request):
    return render(request, "help.html")


def changelog_page(request):
    return render(request, "changelog.html")


def login_page(request):
    if request.method == "POST":
        user = authenticate(
         username=request.POST["username"],
         password=request.POST["password"]
        )
        login(request, user)
        return redirect("/")
    return render(request, "login.html")
