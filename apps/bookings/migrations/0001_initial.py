from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("trips", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="Booking",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("reference", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("status", models.CharField(choices=[("pending", "Pendente"), ("paid", "Pago"), ("cancelled", "Cancelado")], default="pending", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("paid_at", models.DateTimeField(blank=True, null=True)),
                ("passenger", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="bookings", to=settings.AUTH_USER_MODEL)),
                ("trip", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="bookings", to="trips.trip")),
                ("trip_seat", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="booking", to="trips.tripseat")),
            ],
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("provider", models.CharField(max_length=20)),
                ("transaction_reference", models.CharField(max_length=100)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("status", models.CharField(default="submitted", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("booking", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="payments", to="bookings.booking")),
            ],
        ),
    ]
