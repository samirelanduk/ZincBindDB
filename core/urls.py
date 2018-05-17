from django.urls import path
import core.views as core_views

urlpatterns = [
 path(r"", core_views.home),
]
