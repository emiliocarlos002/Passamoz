from django import forms
from django.utils import timezone
from .models import PaymentAccount, Route, Transporter, Vehicle

class TransporterApplicationForm(forms.ModelForm):
    class Meta:
        model = Transporter
        fields = (
            "name", "legal_name", "registration_number", "company_type",
            "founded_year", "fleet_size", "province", "city", "address",
            "main_terminal", "responsible_name", "responsible_role",
            "phone", "whatsapp", "email", "website", "vehicle_types",
            "operating_provinces",
        )
        labels = {
            "name": "Nome da empresa",
            "legal_name": "Nome legal",
            "registration_number": "NUIT / número de registo",
            "company_type": "Tipo de empresa",
            "founded_year": "Ano de fundação",
            "fleet_size": "Número aproximado de autocarros",
            "province": "Província",
            "city": "Cidade",
            "address": "Endereço completo",
            "main_terminal": "Terminal principal",
            "responsible_name": "Nome completo do responsável",
            "responsible_role": "Cargo do responsável",
            "phone": "Telefone principal",
            "whatsapp": "WhatsApp",
            "email": "E-mail empresarial",
            "website": "Website (opcional)",
            "vehicle_types": "Tipos de veículos",
            "operating_provinces": "Províncias onde opera",
        }
        widgets = {
            "company_type": forms.Select(choices=[
                ("", "Selecione o tipo"),
                ("sociedade", "Sociedade comercial"),
                ("empresario", "Empresário em nome individual"),
                ("cooperativa", "Cooperativa"),
                ("outra", "Outra"),
            ]),
            "province": forms.Select(choices=[
                ("", "Selecione a província"),
                ("Maputo Cidade", "Maputo Cidade"), ("Maputo Província", "Maputo Província"),
                ("Gaza", "Gaza"), ("Inhambane", "Inhambane"), ("Sofala", "Sofala"),
                ("Manica", "Manica"), ("Tete", "Tete"), ("Zambézia", "Zambézia"),
                ("Nampula", "Nampula"), ("Cabo Delgado", "Cabo Delgado"), ("Niassa", "Niassa"),
            ]),
            "founded_year": forms.NumberInput(attrs={"min": 1900, "max": timezone.now().year, "placeholder": "Ex.: 2015"}),
            "fleet_size": forms.NumberInput(attrs={"min": 1, "placeholder": "Ex.: 25"}),
            "website": forms.URLInput(attrs={"placeholder": "https://..."}),
            "vehicle_types": forms.TextInput(attrs={"placeholder": "Ex.: Machimbombos, mini-buses"}),
            "operating_provinces": forms.TextInput(attrs={"placeholder": "Ex.: Maputo, Gaza, Sofala"}),
        }

    def clean_founded_year(self):
        year = self.cleaned_data.get("founded_year")
        if year and year > timezone.now().year:
            raise forms.ValidationError("O ano de fundação não pode estar no futuro.")
        return year

    def clean_fleet_size(self):
        value = self.cleaned_data.get("fleet_size")
        if value is not None and value < 1:
            raise forms.ValidationError("Informe pelo menos 1 autocarro.")
        return value

class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ("origin", "destination", "active")

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ("name", "registration_plate", "capacity", "active")

class PaymentAccountForm(forms.ModelForm):
    class Meta:
        model = PaymentAccount
        fields = (
            "provider",
            "account_name",
            "account_number",
            "is_active",
            "integration_mode",
            "payment_instructions",
            "gateway_wallet_id",
        )
