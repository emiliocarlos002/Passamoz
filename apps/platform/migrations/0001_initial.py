from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [("transporters", "0001_initial")]
    operations = [
        migrations.CreateModel(
            name="MonthlySubscription",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("reference_month", models.DateField()),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("due_date", models.DateField()),
                ("status", models.CharField(choices=[("pending", "Pendente"), ("paid", "Paga"), ("overdue", "Em atraso"), ("cancelled", "Cancelada")], default="pending", max_length=20)),
                ("paid_at", models.DateTimeField(blank=True, null=True)),
                ("payment_reference", models.CharField(blank=True, max_length=100)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("transporter", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="subscriptions", to="transporters.transporter")),
            ],
        ),
        migrations.AddConstraint(
            model_name="monthlysubscription",
            constraint=models.UniqueConstraint(fields=("transporter", "reference_month"), name="unique_monthly_subscription"),
        ),
    ]
