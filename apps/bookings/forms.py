from django import forms

class PaymentConfirmationForm(forms.Form):
    provider = forms.ChoiceField(
        choices=[
            ("mpesa", "M-Pesa"),
            ("emola", "e-Mola"),
            ("mkesh", "mKesh"),
        ]
    )
    transaction_reference = forms.CharField(max_length=100)
