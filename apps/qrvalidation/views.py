import json
import uuid

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from apps.bookings.models import Booking
from apps.tickets.models import Ticket
from apps.transporters.models import Transporter


def get_operator(user):
    transporter = getattr(user, "transporter_profile", None)
    if transporter and transporter.status == Transporter.Status.ACTIVE:
        return transporter
    return None


@login_required(login_url="/conta/entrar/")
def scanner(request):
    operator = get_operator(request.user)
    if operator is None:
        return JsonResponse({"detail": "Acesso reservado a operadoras ativas."}, status=403)
    return render(request, "qrvalidation/scanner.html", {"operator": operator})


@login_required(login_url="/conta/entrar/")
@require_POST
def validate(request):
    operator = get_operator(request.user)
    if operator is None:
        return JsonResponse({"valid": False, "message": "Acesso não autorizado."}, status=403)

    try:
        payload = json.loads(request.body or "{}")
        raw_code = str(payload.get("code", "")).strip()
        code = uuid.UUID(raw_code)
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({
            "valid": False,
            "message": "QR Code inválido.",
        }, status=400)

    try:
        ticket = (
            Ticket.objects.select_related(
                "booking__passenger",
                "booking__trip__route",
                "booking__trip__transporter",
                "booking__trip_seat__seat",
            )
            .get(code=code)
        )
    except Ticket.DoesNotExist:
        return JsonResponse({"valid": False, "message": "Bilhete não encontrado."}, status=404)

    booking = ticket.booking
    trip = booking.trip

    if trip.transporter_id != operator.id:
        return JsonResponse({
            "valid": False,
            "message": "Este bilhete pertence a outra operadora.",
        }, status=403)

    if booking.status != Booking.Status.PAID:
        return JsonResponse({
            "valid": False,
            "message": "Bilhete ainda não está pago/confirmado.",
            "ticket": ticket.code,
        }, status=409)

    if trip.status == trip.Status.CANCELLED:
        return JsonResponse({
            "valid": False,
            "message": "Esta viagem foi cancelada.",
        }, status=409)

    if trip.status == trip.Status.FINISHED:
        return JsonResponse({
            "valid": False,
            "message": "Esta viagem já foi encerrada.",
        }, status=409)

    passenger = booking.passenger
    return JsonResponse({
        "valid": True,
        "message": "Bilhete válido. Passageiro autorizado para embarque.",
        "ticket": str(ticket.code),
        "passenger": passenger.get_full_name() or passenger.username,
        "phone": getattr(getattr(passenger, "passenger_profile", None), "phone", ""),
        "route": f"{trip.route.origin} → {trip.route.destination}",
        "departure": trip.departure_at.strftime("%d/%m/%Y %H:%M"),
        "seat": booking.trip_seat.seat.seat_number,
        "amount": str(booking.amount),
        "currency": trip.currency,
    })
