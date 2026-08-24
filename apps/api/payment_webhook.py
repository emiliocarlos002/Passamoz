import hashlib
import hmac
import json
import os

from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from apps.bookings.models import Payment
from apps.bookings.services import confirm_payment, expire_booking


@csrf_exempt
def payment_webhook(request):
    if request.method != "POST":
        return HttpResponse(status=405)
    body = request.body
    token = os.getenv("PAYMENT_WEBHOOK_TOKEN", "").strip()
    signature = request.headers.get("X-Passamoz-Webhook-Signature", "").strip()
    if token:
        expected = hmac.new(token.encode(), body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            # Backward-compatible token header for gateways that cannot sign yet.
            if request.headers.get("X-Passamoz-Webhook-Token") != token:
                return HttpResponse(status=401)
    try:
        payload = json.loads(body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "invalid_json"}, status=400)

    gateway_ref = str(payload.get("id") or payload.get("reference") or payload.get("charge_id") or "")
    status = str(payload.get("status") or "").lower()
    event_id = str(payload.get("event_id") or payload.get("eventId") or payload.get("idempotency_key") or "")
    if not gateway_ref:
        return JsonResponse({"ok": False, "error": "missing_reference"}, status=400)

    with transaction.atomic():
        payment = Payment.objects.select_for_update().filter(gateway_reference=gateway_ref).first()
        if not payment:
            return JsonResponse({"ok": True, "ignored": True})
        if event_id and payment.webhook_event_id == event_id:
            return JsonResponse({"ok": True, "duplicate": True})
        payment.gateway_status = status
        if event_id:
            payment.webhook_event_id = event_id
        payment.save(update_fields=["gateway_status", "webhook_event_id", "updated_at"])

    if status in {"paid", "success", "succeeded", "completed"}:
        booking, ticket = confirm_payment(payment.pk)
        if ticket and not ticket.pdf:
            from apps.passengerpanel.services import create_ticket_artifacts
            create_ticket_artifacts(ticket)
    elif status in {"failed", "cancelled", "canceled", "rejected", "expired"}:
        with transaction.atomic():
            payment = Payment.objects.select_for_update().get(pk=payment.pk)
            payment.status = "rejected"
            payment.save(update_fields=["status", "updated_at"])
            booking = payment.booking
            if booking.status == booking.Status.PENDING or booking.status == booking.Status.PAYMENT_PROCESSING:
                booking.status = booking.Status.CANCELLED
                booking.cancelled_at = timezone.now()
                booking.save(update_fields=["status", "cancelled_at"])
                seat = booking.trip_seat
                seat.is_available = True
                seat.save(update_fields=["is_available"])
    return JsonResponse({"ok": True})
