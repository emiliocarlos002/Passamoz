from django.urls import path

from .views import scanner, validate

app_name = "qrvalidation"

urlpatterns = [
    path("", scanner, name="scanner"),
    path("validar/", validate, name="validate"),
]
