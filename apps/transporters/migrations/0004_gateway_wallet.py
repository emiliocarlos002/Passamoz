from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("transporters", "0003_paymentaccount_integration")]
    operations = [migrations.AddField(model_name="paymentaccount", name="gateway_wallet_id", field=models.CharField(blank=True, help_text="Identificador público da carteira no gateway; nunca guardar a chave secreta aqui.", max_length=100))]
