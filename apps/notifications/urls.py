from django.urls import path

from .views import list_notifications, mark_all_read, mark_read

app_name = "notifications"

urlpatterns = [
    path("", list_notifications, name="list"),
    path("<int:pk>/ler/", mark_read, name="mark-read"),
    path("marcar-todas-lidas/", mark_all_read, name="mark-all-read"),
]
