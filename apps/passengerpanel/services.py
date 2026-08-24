from io import BytesIO
from pathlib import Path

import qrcode
from django.conf import settings
from django.core.files.base import ContentFile
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from apps.tickets.models import Ticket


def create_ticket_artifacts(ticket: Ticket) -> None:
    booking = ticket.booking
    trip = booking.trip
    passenger = booking.passenger
    passenger_name = passenger.get_full_name() or passenger.username
    route = f"{trip.route.origin} → {trip.route.destination}"
    code = str(ticket.code)

    qr_buffer = BytesIO()
    qr = qrcode.make(code)
    qr.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)

    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=A4)
    width, height = A4
    pdf.setTitle(f"Bilhete PassaMoz {code}")

    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(50, height - 60, "PassaMoz")
    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(50, height - 95, "Bilhete de Viagem")

    pdf.setFont("Helvetica", 11)
    rows = [
        ("Passageiro", passenger_name),
        ("Operadora", trip.transporter.name),
        ("Rota", route),
        ("Partida", trip.departure_at.strftime("%d/%m/%Y %H:%M")),
        ("Chegada", trip.arrival_at.strftime("%d/%m/%Y %H:%M") if trip.arrival_at else "—"),
        ("Lugar", trip_seat_label(booking)),
        ("Valor", f"{booking.amount} {trip.currency}"),
        ("Referência", str(booking.reference)),
        ("Código", code),
    ]
    y = height - 145
    for label, value in rows:
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(50, y, f"{label}:")
        pdf.setFont("Helvetica", 10)
        pdf.drawString(125, y, value[:90])
        y -= 22

    qr_image = ImageReader(qr_buffer)
    pdf.drawImage(qr_image, width - 190, height - 315, 130, 130, preserveAspectRatio=True)
    pdf.setFont("Helvetica", 9)
    pdf.drawString(width - 190, height - 330, "Apresente este QR Code no embarque.")
    pdf.showPage()
    pdf.save()
    pdf_buffer.seek(0)

    filename = f"passamoz-{code}.pdf"
    ticket.pdf.save(filename, ContentFile(pdf_buffer.read()), save=True)


def trip_seat_label(booking) -> str:
    return booking.trip_seat.seat.seat_number
