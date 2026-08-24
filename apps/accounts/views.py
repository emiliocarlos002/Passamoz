from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeDoneView, PasswordChangeView,
    PasswordResetCompleteView, PasswordResetConfirmView, PasswordResetDoneView, PasswordResetView,
)
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View

from apps.transporters.models import Transporter
from .forms import AccountSettingsForm, PassengerRegistrationForm

class HomeView(View):
    def get(self, request):
        # The homepage can show real active operators when they exist.
        operators = Transporter.objects.filter(status=Transporter.Status.ACTIVE).order_by("name")[:8]
        return render(request, "home.html", {"operators": operators})

class PassengerRegisterView(View):
    template_name = "accounts/register.html"

    def get(self, request):
        return render(request, self.template_name, {"form": PassengerRegistrationForm()})

    def post(self, request):
        form = PassengerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
        return render(request, self.template_name, {"form": form})

class PassengerLoginView(LoginView):
    template_name = "accounts/login.html"

class PassengerLogoutView(LogoutView):
    pass

@login_required(login_url="/conta/entrar/")
def account_settings(request):
    if request.method == "POST":
        form = AccountSettingsForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "As suas definições foram atualizadas.")
            return redirect("account-settings")
    else:
        form = AccountSettingsForm(user=request.user)
    return render(request, "accounts/settings.html", {"form": form})

class PassengerPasswordChangeView(PasswordChangeView):
    template_name = "accounts/password_change.html"
    success_url = reverse_lazy("password_change_done")

class PassengerPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = "accounts/password_change_done.html"

class PassengerPasswordResetView(PasswordResetView):
    template_name = "accounts/password_reset.html"
    email_template_name = "accounts/password_reset_email.txt"
    subject_template_name = "accounts/password_reset_subject.txt"
    success_url = reverse_lazy("password_reset_done")

class PassengerPasswordResetDoneView(PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"

class PassengerPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    success_url = reverse_lazy("password_reset_complete")

class PassengerPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"
