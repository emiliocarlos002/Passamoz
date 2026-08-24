from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [("transporters", "0001_initial")]
    operations = [
        migrations.CreateModel(
            name="Trip",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("departure_at", models.DateTimeField()),
                ("arrival_at", models.DateTimeField(blank=True, null=True)),
                ("price", models.DecimalField(decimal_places=2, max_digits=12)),
                ("currency", models.CharField(default="MZN", max_length=3)),
                ("status", models.CharField(choices=[("draft", "Rascunho"), ("published", "Publicada"), ("cancelled", "Cancelada"), ("finished", "Finalizada")], default="draft", max_length=20)),
                ("route", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="trips", to="transporters.route")),
                ("transporter", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="trips", to="transporters.transporter")),
                ("vehicle", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="trips", to="transporters.vehicle")),
            ],
        ),
        migrations.CreateModel(
            name="TripSeat",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("is_available", models.BooleanField(default=True)),
                ("seat", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="transporters.seat")),
                ("trip", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="trip_seats", to="trips.trip")),
            ],
        ),
        migrations.AddConstraint(
            model_name="tripseat",
            constraint=models.UniqueConstraint(fields=("trip", "seat"), name="unique_trip_seat"),
        ),
    ]
