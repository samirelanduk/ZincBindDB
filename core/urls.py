from django.urls import path, include
import core.views as core_views
import zinc.views as zinc_views

urlpatterns = [
 path(r"search", zinc_views.search),
 path(r"search/", zinc_views.search),
 path(r"data/", core_views.data),
 path(r"about/", core_views.about),
 path(r"changelog/", core_views.changelog),
 path(r"pdbs/<slug:code>/", zinc_views.pdb),
 path(r"<slug:pk>/", zinc_views.zinc_site),
 path(r"", core_views.home),
]
