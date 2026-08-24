from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("transporters", "0005_operator_activation")]

    operations = [
        migrations.AddField(model_name="transporter", name="province", field=models.CharField(blank=True, max_length=80)),
        migrations.AddField(model_name="transporter", name="city", field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name="transporter", name="main_terminal", field=models.CharField(blank=True, max_length=150)),
        migrations.AddField(model_name="transporter", name="company_type", field=models.CharField(blank=True, max_length=50)),
        migrations.AddField(model_name="transporter", name="founded_year", field=models.PositiveIntegerField(blank=True, null=True)),
        migrations.AddField(model_name="transporter", name="fleet_size", field=models.PositiveIntegerField(blank=True, null=True)),
        migrations.AddField(model_name="transporter", name="responsible_name", field=models.CharField(blank=True, max_length=150)),
        migrations.AddField(model_name="transporter", name="responsible_role", field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name="transporter", name="whatsapp", field=models.CharField(blank=True, max_length=30)),
        migrations.AddField(model_name="transporter", name="website", field=models.URLField(blank=True)),
        migrations.AddField(model_name="transporter", name="vehicle_types", field=models.CharField(blank=True, max_length=255)),
        migrations.AddField(model_name="transporter", name="operating_provinces", field=models.CharField(blank=True, max_length=255)),
    ]
