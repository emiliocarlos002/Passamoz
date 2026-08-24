from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("transporters", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="paymentaccount",
            name="provider",
            field=models.CharField(
                choices=[
                    ("mpesa", "M-Pesa"),
                    ("emola", "e-Mola"),
                    ("mkesh", "mKesh"),
                    ("bank", "Transferência bancária"),
                ],
                max_length=20,
            ),
        ),
    ]
