"""URL redirects for ZincBind."""

from django.conf.urls import url
import zincbind.views as views

urlpatterns = [
 url(r"^data/$", views.data),
 url(r"^$", views.home)
]
