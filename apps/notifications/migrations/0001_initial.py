from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("bookings", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("kind", models.CharField(choices=[("payment_confirmed", "Pagamento confirmado"), ("payment_rejected", "Pagamento rejeitado"), ("general", "Geral")], default="general", max_length=40)),
                ("title", models.CharField(max_length=160)),
                ("message", models.TextField()),
                ("is_read", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("booking", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="notifications", to="bookings.booking")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notifications", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ("-created_at",),
                "indexes": [
                    models.Index(fields=["user", "is_read"], name="notificati_user_id_0a5f7e_idx"),
                    models.Index(fields=["user", "created_at"], name="notificati_user_id_7f2b5d_idx"),
                ],
            },
        ),
    ]
