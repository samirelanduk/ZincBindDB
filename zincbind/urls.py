"""URL redirects for ZincBind."""

from django.conf.urls import url
import zincbind.views as views

urlpatterns = [
 url(r"^data/$", views.data),
 url(r"^search", views.search),
 url(r"^changelog", views.changelog),
 url(r"^ngl/(.+?)/$", views.ngl_site),
 url(r"^(.+?)/$", views.site),
 url(r"^$", views.home)
]
