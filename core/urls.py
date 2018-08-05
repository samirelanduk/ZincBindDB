from django.urls import path, include
import core.views as core_views
import zinc.views as zinc_views

urlpatterns = [
 path(r"api/<slug:type>/<slug:pk>/", zinc_views.api_object),
 path(r"api/pdbs/", zinc_views.PdbViewSet.as_view({"get": "list"})),
 path(r"api/sites/", zinc_views.ZincSiteViewSet.as_view({"get": "list"})),
 path(r"api/chain-clusters/", zinc_views.ChainClusterViewSet.as_view({"get": "list"})),
 path(r"api/site-clusters/", zinc_views.ZincSiteClusterViewSet.as_view({"get": "list"})),
 path(r"api/", zinc_views.api),
 path(r"search", zinc_views.search),
 path(r"search/", zinc_views.search),
 path(r"data/", core_views.data),
 path(r"data/all/", core_views.all_data),
 path(r"about/", core_views.about),
 path(r"help/", core_views.help),
 path(r"changelog/", core_views.changelog),
 path(r"pdbs/<slug:code>/", zinc_views.pdb),
 path(r"<slug:pk>/", zinc_views.zinc_site),
 path(r"", core_views.home),
]
