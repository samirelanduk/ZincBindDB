from django.urls import path
import core.views as core_views
import zinc.views as zinc_views

urlpatterns = [
 path(r"search", zinc_views.search),
 path(r"search/", zinc_views.search),
 path(r"pdbs/<slug:code>/", zinc_views.pdb),
 path(r"<slug:pk>/", zinc_views.zinc_site),
 path(r"", core_views.home),
]
