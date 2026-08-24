from django.urls import path
from .views import TicketDetailView

urlpatterns = [
    path("<uuid:reference>/", TicketDetailView.as_view(), name="ticket-detail"),
]
