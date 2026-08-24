from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.accounts.models import PassengerProfile
from apps.bookings.models import Booking, Payment, BookingPassenger
from apps.bookings.services import booking_expiry, confirm_payment, expire_booking
from apps.tickets.models import Ticket
from apps.transporters.models import PaymentAccount, Route
from apps.bookings.gateway import GatewayError, NetShopGateway
from apps.trips.models import Trip, TripSeat

from .services import create_ticket_artifacts


def passenger_required(view):
    @login_required(login_url="/conta/entrar/")
    def wrapped(request, *args, **kwargs):
        if not PassengerProfile.objects.filter(user=request.user).exists():
            raise Http404("Perfil de passageiro não encontrado.")
        return view(request, *args, **kwargs)
    return wrapped


@passenger_required
def dashboard(request):
    bookings = (
        Booking.objects.filter(passenger=request.user)
        .select_related("trip__route", "trip__transporter", "trip_seat__seat")
        .order_by("-created_at")
    )
    return render(request, "passengerpanel/dashboard.html", {
        "bookings": bookings[:8],
        "paid_count": bookings.filter(status=Booking.Status.PAID).count(),
        "pending_count": bookings.filter(status=Booking.Status.PENDING).count(),
    })



@passenger_required
def my_trips(request):
    bookings = (
        Booking.objects.filter(passenger=request.user)
        .select_related("trip__route", "trip__transporter", "trip_seat__seat")
        .order_by("-trip__departure_at")
    )
    return render(request, "passengerpanel/my_trips.html", {"bookings": bookings})


@passenger_required
def payments(request):
    payments_qs = (
        Payment.objects.filter(booking__passenger=request.user)
        .select_related("booking__trip__route", "booking__trip__transporter")
        .order_by("-created_at")
    )
    return render(request, "passengerpanel/payments.html", {"payments": payments_qs})


@passenger_required
def favorites(request):
    ids = request.session.get("passamoz_favorites", [])
    trips = list(Trip.objects.filter(pk__in=ids, status=Trip.Status.PUBLISHED).select_related("route", "transporter", "vehicle"))
    order = {int(pk): i for i, pk in enumerate(ids)}
    trips.sort(key=lambda trip: order.get(trip.pk, 999999))
    return render(request, "passengerpanel/favorites.html", {"trips": trips})


@passenger_required
@require_POST
def toggle_favorite(request, pk):
    get_object_or_404(Trip, pk=pk, status=Trip.Status.PUBLISHED)
    ids = [int(x) for x in request.session.get("passamoz_favorites", [])]
    if pk in ids:
        ids.remove(pk)
        messages.success(request, "Viagem removida dos favoritos.")
    else:
        ids.append(pk)
        messages.success(request, "Viagem adicionada aos favoritos.")
    request.session["passamoz_favorites"] = ids
    return redirect("passengerpanel:trip-detail", pk=pk)


def promotions(request):
    return render(request, "passengerpanel/promotions.html")


def help_page(request):
    return render(request, "passengerpanel/help.html")


def about_page(request):
    return render(request, "passengerpanel/about.html")


def search_trips(request):
    trips = Trip.objects.filter(
        status=Trip.Status.PUBLISHED,
        departure_at__gte=timezone.now(),
    ).select_related("route", "transporter", "vehicle")

    origin = request.GET.get("origin", "").strip()
    destination = request.GET.get("destination", "").strip()
    date = request.GET.get("date", "").strip()

    if origin:
        trips = trips.filter(route__origin__icontains=origin)
    if destination:
        trips = trips.filter(route__destination__icontains=destination)
    if date:
        trips = trips.filter(departure_at__date=date)

    trips = trips.annotate(
        available_count=__import__("django.db.models", fromlist=["Count"]).Count(
            "trip_seats", filter=Q(trip_seats__is_available=True)
        )
    ).filter(available_count__gt=0).order_by("departure_at")

    return render(request, "passengerpanel/search.html", {
        "trips": trips, "origin": origin, "destination": destination, "date": date,
    })


def trip_detail(request, pk):
    trip = get_object_or_404(
        Trip.objects.select_related("route", "transporter", "vehicle"),
        pk=pk,
        status=Trip.Status.PUBLISHED,
    )
    seats = trip.trip_seats.select_related("seat").filter(is_available=True)
    accounts = trip.transporter.payment_accounts.filter(is_active=True).order_by("provider")
    favorite_ids = request.session.get("passamoz_favorites", [])
    return render(request, "passengerpanel/trip_detail.html", {
        "trip": trip, "seats": seats, "payment_accounts": accounts,
        "is_favorite": trip.pk in [int(x) for x in favorite_ids],
    })


@passenger_required
@require_POST
def create_booking(request, pk):
    trip = get_object_or_404(
        Trip.objects.select_related("transporter"),
        pk=pk,
        status=Trip.Status.PUBLISHED,
    )
    seat_id = request.POST.get("seat_id")
    with transaction.atomic():
        trip_seat = get_object_or_404(
            TripSeat.objects.select_related("seat").select_for_update(),
            pk=seat_id, trip=trip, is_available=True,
        )
        # Lock the seat before creating the booking: two simultaneous requests cannot win it.
        if Booking.objects.filter(trip_seat=trip_seat, status__in=[Booking.Status.PENDING, Booking.Status.PAYMENT_PROCESSING, Booking.Status.PAID]).exists():
            messages.error(request, "Este lugar acabou de ser reservado.")
            return redirect("passengerpanel:trip-detail", pk=trip.pk)
        booking = Booking.objects.create(
            passenger=request.user, trip=trip, trip_seat=trip_seat, amount=trip.price,
            status=Booking.Status.PENDING, expires_at=booking_expiry(),
        )
        BookingPassenger.objects.create(
            booking=booking, trip_seat=trip_seat,
            full_name=request.user.get_full_name() or request.user.username,
            phone=getattr(request.user, "phone", "") or "", passenger_type="adult",
        )
        trip_seat.is_available = False
        trip_seat.save(update_fields=["is_available"])

    messages.success(request, "Reserva criada. O lugar ficará bloqueado por 15 minutos para pagamento.")
    return redirect("passengerpanel:payment", reference=booking.reference)


@passenger_required
def payment(request, reference):
    booking = get_object_or_404(
        Booking.objects.select_related(
            "trip__route", "trip__transporter", "trip_seat__seat"
        ),
        reference=reference,
        passenger=request.user,
    )
    if booking.expires_at and booking.expires_at <= timezone.now() and booking.status in {Booking.Status.PENDING, Booking.Status.PAYMENT_PROCESSING}:
        expire_booking(booking)
        booking.refresh_from_db()
    accounts = booking.trip.transporter.payment_accounts.filter(is_active=True)
    return render(request, "passengerpanel/payment.html", {
        "booking": booking, "accounts": accounts,
    })


@passenger_required
@require_POST
def submit_payment(request, reference):
    booking = get_object_or_404(
        Booking.objects.select_related("trip__transporter"),
        reference=reference,
        passenger=request.user,
    )
    if booking.expires_at and booking.expires_at <= timezone.now() and booking.status in {Booking.Status.PENDING, Booking.Status.PAYMENT_PROCESSING}:
        expire_booking(booking)
        booking.refresh_from_db()
    if booking.status != Booking.Status.PENDING:
        messages.info(request, "Esta reserva já não está pendente.")
        return redirect("passengerpanel:my-tickets")

    provider = request.POST.get("provider", "").strip()
    transaction_reference = request.POST.get("transaction_reference", "").strip()
    payer_phone = request.POST.get("payer_phone", "").strip()
    account = get_object_or_404(
        PaymentAccount, transporter=booking.trip.transporter, provider=provider, is_active=True
    )

    if account.integration_mode == "gateway":
        if provider not in {"mpesa", "emola", "mkesh"}:
            messages.error(request, "Este método não está disponível no gateway.")
            return redirect("passengerpanel:payment", reference=reference)
        if not account.gateway_wallet_id:
            messages.error(request, "A operadora ainda não configurou a carteira do gateway.")
            return redirect("passengerpanel:payment", reference=reference)
        if not payer_phone:
            messages.error(request, "Informe o número da carteira que fará o pagamento.")
            return redirect("passengerpanel:payment", reference=reference)

        payment, created = Payment.objects.get_or_create(
            booking=booking, provider=provider, transaction_reference=f"PMZ-{booking.reference}",
            defaults={"amount": booking.amount, "payer_phone": payer_phone, "status": "processing", "idempotency_key": f"PMZ-{booking.reference}"},
        )
        if not created and payment.status in {"confirmed", "processing"}:
            messages.info(request, "Este pagamento já está em processamento.")
            return redirect("passengerpanel:payments")
        try:
            result = NetShopGateway().create_charge(
                wallet_id=account.gateway_wallet_id,
                amount=booking.amount, method=provider, msisdn=payer_phone,
                reference=f"PMZ-{booking.reference}",
            )
        except GatewayError as exc:
            payment.status = "failed"
            payment.gateway_status = "error"
            payment.save(update_fields=["status", "gateway_status"])
            messages.error(request, str(exc))
            return redirect("passengerpanel:payment", reference=reference)
        payment.gateway_reference = result["reference"]
        payment.gateway_status = result["status"]
        payment.payer_phone = payer_phone
        payment.status = "confirmed" if result["status"] in {"paid", "success", "succeeded", "completed"} else "processing"
        payment.save(update_fields=["gateway_reference", "gateway_status", "payer_phone", "status", "updated_at"])
        if payment.status == "confirmed":
            booking, ticket = confirm_payment(payment.pk)
            if ticket and not ticket.pdf:
                create_ticket_artifacts(ticket)
        messages.success(request, "Pagamento enviado. O estado será atualizado automaticamente quando o gateway confirmar a transação.")
        return redirect("passengerpanel:payments")

    if not transaction_reference:
        messages.error(request, "Informe a referência da transação.")
        return redirect("passengerpanel:payment", reference=reference)
    if Payment.objects.filter(provider=provider, transaction_reference=transaction_reference).exists():
        messages.error(request, "Esta referência de pagamento já foi utilizada.")
        return redirect("passengerpanel:payment", reference=reference)
    Payment.objects.create(booking=booking, provider=provider, transaction_reference=transaction_reference, amount=booking.amount, payer_phone=payer_phone, status="submitted")
    messages.success(request, "Pagamento registado. A operadora irá validar a referência.")
    return redirect("passengerpanel:payments")


@passenger_required
def my_tickets(request):
    bookings = (
        Booking.objects.filter(passenger=request.user)
        .select_related(
            "trip__route", "trip__transporter", "trip_seat__seat", "ticket"
        )
        .order_by("-created_at")
    )
    return render(request, "passengerpanel/tickets.html", {"bookings": bookings})


@passenger_required
def ticket_detail(request, reference):
    booking = get_object_or_404(
        Booking.objects.select_related(
            "trip__route", "trip__transporter", "trip_seat__seat", "ticket"
        ),
        reference=reference,
        passenger=request.user,
        status=Booking.Status.PAID,
    )
    if not hasattr(booking, "ticket"):
        with transaction.atomic():
            ticket, _ = Ticket.objects.get_or_create(booking=booking)
            create_ticket_artifacts(ticket)
    else:
        ticket = booking.ticket
        if not ticket.pdf:
            create_ticket_artifacts(ticket)

    return render(request, "passengerpanel/ticket_detail.html", {
        "booking": booking, "ticket": ticket,
    })


@passenger_required
def ticket_pdf(request, reference):
    booking = get_object_or_404(
        Booking.objects.select_related("ticket"),
        reference=reference,
        passenger=request.user,
        status=Booking.Status.PAID,
    )
    ticket = getattr(booking, "ticket", None)
    if ticket is None:
        ticket = Ticket.objects.create(booking=booking)
        create_ticket_artifacts(ticket)
    elif not ticket.pdf:
        create_ticket_artifacts(ticket)

    if not ticket.pdf:
        raise Http404("PDF do bilhete não disponível.")
    return FileResponse(
        ticket.pdf.open("rb"),
        as_attachment=True,
        filename=f"passamoz-{ticket.code}.pdf",
    )
