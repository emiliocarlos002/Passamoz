from io import BytesIO
import qrcode
from django.core.files.base import ContentFile
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from .models import Ticket

def create_ticket(booking):
    ticket, _ = Ticket.objects.get_or_create(booking=booking)

    qr = qrcode.make(str(ticket.code))
    qr_buffer = BytesIO()
    qr.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)

    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=A4)
    pdf.setTitle(f"Bilhete {ticket.code}")
    pdf.drawString(50, 790, "BILHETE DE PASSAGEM")
    pdf.drawString(50, 755, f"Passageiro: {booking.passenger.get_full_name()}")
    pdf.drawString(
        50,
        735,
        f"Rota: {booking.trip.route.origin} -> {booking.trip.route.destination}",
    )
    pdf.drawString(
        50,
        715,
        f"Data: {booking.trip.departure_at:%d/%m/%Y %H:%M}",
    )
    pdf.drawString(
        50,
        695,
        f"Lugar: {booking.trip_seat.seat.seat_number}",
    )
    pdf.drawString(
        50,
        675,
        f"Operadora: {booking.trip.transporter.name}",
    )
    pdf.drawString(
        50,
        655,
        f"Valor: {booking.amount} {booking.trip.currency}",
    )
    pdf.drawImage(
        ImageReader(qr_buffer),
        50,
        500,
        width=120,
        height=120,
    )
    pdf.drawString(50, 480, f"QR: {ticket.code}")
    pdf.save()

    ticket.pdf.save(
        f"{ticket.code}.pdf",
        ContentFile(pdf_buffer.getvalue()),
        save=True,
    )
    return ticket
