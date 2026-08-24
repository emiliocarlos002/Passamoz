from django.db import migrations, models
from django.db.models import Q
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("bookings", "0002_payment_gateway")]

    operations = [
        migrations.AlterField(
            model_name="booking",
            name="trip_seat",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="bookings",
                to="trips.tripseat",
            ),
        ),
        migrations.AlterField(
            model_name="booking",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pendente"),
                    ("payment_processing", "Pagamento em processamento"),
                    ("paid", "Pago"),
                    ("expired", "Expirado"),
                    ("cancelled", "Cancelado"),
                    ("refunded", "Reembolsado"),
                ],
                default="pending",
                max_length=30,
            ),
        ),
        migrations.AddField(model_name="booking", name="expires_at", field=models.DateTimeField(blank=True, null=True)),
        migrations.AddField(model_name="booking", name="cancelled_at", field=models.DateTimeField(blank=True, null=True)),
        migrations.AddField(model_name="payment", name="idempotency_key", field=models.CharField(blank=True, max_length=150, null=True, unique=True)),
        migrations.AddField(model_name="payment", name="webhook_event_id", field=models.CharField(blank=True, max_length=150, null=True, unique=True)),
        migrations.AddField(model_name="payment", name="updated_at", field=models.DateTimeField(auto_now=True)),
        migrations.AddField(model_name="payment", name="confirmed_at", field=models.DateTimeField(blank=True, null=True)),
        migrations.CreateModel(
            name="BookingPassenger",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(max_length=150)),
                ("phone", models.CharField(blank=True, max_length=30)),
                ("passenger_type", models.CharField(default="adult", max_length=30)),
                ("notes", models.CharField(blank=True, max_length=255)),
                ("booking", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="passengers", to="bookings.booking")),
                ("trip_seat", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="booking_passengers", to="trips.tripseat")),
            ],
        ),
        migrations.AddConstraint(
            model_name="booking",
            constraint=models.UniqueConstraint(
                condition=Q(status__in=["pending", "payment_processing", "paid"]),
                fields=["trip_seat"],
                name="unique_active_booking_per_trip_seat",
            ),
        ),
        migrations.AddConstraint(
            model_name="bookingpassenger",
            constraint=models.UniqueConstraint(fields=["booking", "trip_seat"], name="unique_booking_passenger_seat"),
        ),
        migrations.AddConstraint(
            model_name="payment",
            constraint=models.UniqueConstraint(fields=["provider", "transaction_reference"], name="unique_payment_transaction_reference"),
        ),
        migrations.AddIndex(model_name="booking", index=models.Index(fields=["status", "expires_at"], name="bookings_b_status_7e8a8f_idx")),
        migrations.AddIndex(model_name="booking", index=models.Index(fields=["passenger", "created_at"], name="bookings_b_passeng_0fbd7d_idx")),
        migrations.AddIndex(model_name="payment", index=models.Index(fields=["gateway_reference"], name="bookings_p_gateway_5a0f5b_idx")),
        migrations.AddIndex(model_name="payment", index=models.Index(fields=["status", "created_at"], name="bookings_p_status_1c3f8d_idx")),
    ]
