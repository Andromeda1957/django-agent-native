"""Root URL configuration.

Project-level routing only. App routes live in each app's urls.py and are
included here.
"""

from django.contrib import admin
from django.urls import include
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("web.urls")),
]
