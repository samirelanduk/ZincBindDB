from django.conf.urls import url
from zincsites import views

urlpatterns = [
 url(r"^new/", views.new_site_page, name="new_site_page"),
]
