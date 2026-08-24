from django.urls import path
from .views import PublishTripView, TripCreateView, TripListView

urlpatterns = [
    path("", TripListView.as_view(), name="trip-list"),
    path("nova/", TripCreateView.as_view(), name="trip-create"),
    path(
        "<int:pk>/publicar/",
        PublishTripView.as_view(),
        name="trip-publish",
    ),
]
