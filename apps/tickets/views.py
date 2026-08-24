from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.views import View
from apps.bookings.models import Booking
from .models import Ticket
from .services import create_ticket

class TicketDetailView(LoginRequiredMixin, View):
    def get(self, request, reference):
        booking = get_object_or_404(
            Booking,
            reference=reference,
            passenger=request.user,
            status=Booking.Status.PAID,
        )
        ticket, _ = Ticket.objects.get_or_create(booking=booking)
        if not ticket.pdf:
            ticket = create_ticket(booking)
        return render(
            request,
            "tickets/detail.html",
            {"ticket": ticket},
        )
