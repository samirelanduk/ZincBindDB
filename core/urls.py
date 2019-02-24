from django.urls import path, include
import core.views as core_views

urlpatterns = [
 path(r"api/<slug:type>/<slug:pk>/", core_views.api_object),
 path(r"api/pdbs/", core_views.PdbViewSet.as_view({"get": "list"})),
 path(r"api/sites/", core_views.ZincSiteViewSet.as_view({"get": "list"})),
 path(r"api/chain-clusters/", core_views.ChainClusterViewSet.as_view({"get": "list"})),
 path(r"api/groups/", core_views.GroupViewSet.as_view({"get": "list"})),
 path(r"api/search", core_views.PdbSearchResults.as_view({"get": "list"})),
 path(r"api/search/", core_views.PdbSearchResults.as_view({"get": "list"})),
 path(r"api/", core_views.api),
 path(r"search", core_views.search),
 path(r"search/", core_views.search),
 path(r"predict/", core_views.predict),
 path(r"predict", core_views.predict),
 path(r"families/", core_views.families),
 path(r"data/", core_views.data),
 path(r"data/all/", core_views.all_data),
 path(r"about/", core_views.about),
 path(r"help/", core_views.help),
 path(r"changelog/", core_views.changelog),
 path(r"pdbs/<slug:code>/", core_views.pdb),
 path(r"groups/<slug:pk>/", core_views.group),
 path(r"<slug:pk>/", core_views.zinc_site),
 path(r"", core_views.home),
]
