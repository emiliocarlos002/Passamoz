from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="Transporter",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150)),
                ("legal_name", models.CharField(blank=True, max_length=200)),
                ("registration_number", models.CharField(blank=True, max_length=100)),
                ("phone", models.CharField(max_length=30)),
                ("email", models.EmailField(max_length=254)),
                ("address", models.CharField(blank=True, max_length=255)),
                ("status", models.CharField(choices=[("pending", "Aguardando aprovação"), ("active", "Ativa"), ("suspended", "Suspensa")], default="pending", max_length=20)),
                ("approved_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("approved_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="approved_transporters", to=settings.AUTH_USER_MODEL)),
                ("owner", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="transporter_profile", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="PaymentAccount",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("provider", models.CharField(choices=[("mpesa", "M-Pesa"), ("emola", "e-Mola"), ("mkesh", "mKesh")], max_length=20)),
                ("account_name", models.CharField(max_length=150)),
                ("account_number", models.CharField(max_length=50)),
                ("is_active", models.BooleanField(default=True)),
                ("transporter", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="payment_accounts", to="transporters.transporter")),
            ],
        ),
        migrations.CreateModel(
            name="Route",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("origin", models.CharField(max_length=150)),
                ("destination", models.CharField(max_length=150)),
                ("active", models.BooleanField(default=True)),
                ("transporter", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="routes", to="transporters.transporter")),
            ],
        ),
        migrations.CreateModel(
            name="Vehicle",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("registration_plate", models.CharField(max_length=30)),
                ("capacity", models.PositiveIntegerField()),
                ("active", models.BooleanField(default=True)),
                ("transporter", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="vehicles", to="transporters.transporter")),
            ],
        ),
        migrations.CreateModel(
            name="Seat",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("seat_number", models.CharField(max_length=10)),
                ("active", models.BooleanField(default=True)),
                ("vehicle", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="seats", to="transporters.vehicle")),
            ],
        ),
        migrations.AddConstraint(
            model_name="paymentaccount",
            constraint=models.UniqueConstraint(fields=("transporter", "provider"), name="unique_transporter_provider"),
        ),
        migrations.AddConstraint(
            model_name="seat",
            constraint=models.UniqueConstraint(fields=("vehicle", "seat_number"), name="unique_vehicle_seat"),
        ),
    ]
