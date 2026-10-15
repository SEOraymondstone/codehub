from django.urls import path

from . import views

app_name = "pages"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("guide/", views.guide, name="guide"),
    path("privacy/", views.privacy, name="privacy"),
    path("healthz/", views.healthz, name="healthz"),
]
