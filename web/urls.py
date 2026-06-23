from django.urls import path

from web import views

app_name = "web"

urlpatterns = [
    path("", views.home, name="home"),
]
