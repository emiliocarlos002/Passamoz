from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import PassengerProfile

User = get_user_model()

class PassengerRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, label="Nome")
    last_name = forms.CharField(max_length=150, required=False, label="Apelido")
    email = forms.EmailField(label="E-mail")
    phone = forms.CharField(max_length=30, label="Telefone")

    class Meta:
        model = User
        fields = (
            "first_name", "last_name", "email", "phone", "password1", "password2",
        )

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        if PassengerProfile.objects.filter(phone=phone).exists():
            raise forms.ValidationError("Este número de telefone já está cadastrado.")
        return phone

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"].lower()
        user.email = self.cleaned_data["email"].lower()
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
            PassengerProfile.objects.create(user=user, phone=self.cleaned_data["phone"])
        return user


class AccountSettingsForm(forms.Form):
    first_name = forms.CharField(max_length=150, label="Nome")
    last_name = forms.CharField(max_length=150, required=False, label="Apelido")
    email = forms.EmailField(label="E-mail")
    phone = forms.CharField(max_length=30, label="Telefone")

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        if user is not None and not self.is_bound:
            profile = getattr(user, "passenger_profile", None)
            self.initial.update({
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone": profile.phone if profile else "",
            })

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("Este e-mail já está sendo usado por outra conta.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        if PassengerProfile.objects.filter(phone=phone).exclude(user=self.user).exists():
            raise forms.ValidationError("Este número de telefone já está sendo usado por outra conta.")
        return phone

    def save(self):
        user = self.user
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        # O projeto usa o e-mail como nome de utilizador. Mantemos ambos sincronizados.
        user.username = self.cleaned_data["email"]
        user.save(update_fields=["first_name", "last_name", "email", "username"])
        profile, _ = PassengerProfile.objects.get_or_create(user=user)
        profile.phone = self.cleaned_data["phone"]
        profile.save(update_fields=["phone"])
        return user
