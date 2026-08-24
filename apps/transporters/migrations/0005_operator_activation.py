from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("transporters", "0004_gateway_wallet"),
    ]

    operations = [
        migrations.AddField(
            model_name="transporter",
            name="activation_issued_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="transporter",
            name="activation_required",
            field=models.BooleanField(default=False),
        ),
    ]
