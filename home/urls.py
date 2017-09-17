from django.conf.urls import url
from home import views

urlpatterns = [
 url(r"^changelog/", views.changelog_page, name="changelog_page"),
 url(r"^help/", views.help_page, name="help_page"),
 url(r"^about/", views.about_page, name="about_page"),
 url(r"^$", views.home_page, name="home_page")
]
