from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("notifications", "0001_initial")]
    operations = [migrations.AlterField(model_name="notification", name="kind", field=models.CharField(max_length=40, choices=[("payment_confirmed", "Pagamento confirmado"), ("payment_rejected", "Pagamento rejeitado"), ("general", "Geral"), ("operator_application", "Candidatura de operadora"), ("operator_decision", "Decisão sobre operadora")], default="general"))]
