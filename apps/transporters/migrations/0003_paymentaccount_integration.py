from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("transporters", "0002_paymentaccount_bank")]
    operations = [
        migrations.AddField(model_name="paymentaccount", name="integration_mode", field=models.CharField(choices=[("manual", "Pagamento por referência"), ("gateway", "Gateway/API")], default="manual", max_length=20)),
        migrations.AddField(model_name="paymentaccount", name="payment_instructions", field=models.TextField(blank=True, help_text="Instruções mostradas ao passageiro.")),
    ]
