from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True
    dependencies = [("bookings", "0001_initial")]
    operations = [
        migrations.CreateModel(
            name="Ticket",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("issued_at", models.DateTimeField(auto_now_add=True)),
                ("pdf", models.FileField(blank=True, upload_to="tickets/")),
                ("booking", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="ticket", to="bookings.booking")),
            ],
        ),
    ]
