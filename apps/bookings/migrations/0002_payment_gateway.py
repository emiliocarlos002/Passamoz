from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("bookings", "0001_initial")]
    operations = [
        migrations.AddField(
            model_name="payment",
            name="gateway_reference",
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name="payment",
            name="gateway_status",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="payment",
            name="payer_phone",
            field=models.CharField(blank=True, max_length=30),
        ),
    ]
