from django.shortcuts import render

def home_page(request):
    return render(request, "home.html")


def about_page(request):
    return render(request, "about.html")


def help_page(request):
    return render(request, "help.html")


def changelog_page(request):
    return render(request, "changelog.html")


def login_page(request):
    return render(request, "login.html")
