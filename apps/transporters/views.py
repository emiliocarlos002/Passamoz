from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.views import View
from apps.notifications.services import notify_staff_new_transporter
from .forms import (
    PaymentAccountForm,
    RouteForm,
    TransporterApplicationForm,
    VehicleForm,
)
from .models import Transporter
from .services import generate_vehicle_seats

class TransporterRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        try:
            self.transporter = request.user.transporter_profile
        except Transporter.DoesNotExist as exc:
            raise PermissionDenied("Esta conta não possui uma operadora.") from exc
        if self.transporter.status != Transporter.Status.ACTIVE:
            raise PermissionDenied("A operadora ainda não está ativa.")
        if self.transporter.activation_required:
            messages.info(request, "Ative a sua conta através do link enviado para o seu e-mail antes de acessar o painel.")
            return redirect("transporter-apply")
        return super().dispatch(request, *args, **kwargs)

class ApplyTransporterView(LoginRequiredMixin, View):
    def get(self, request):
        if hasattr(request.user, "transporter_profile"):
            return render(request, "transporters/apply.html", {"form": TransporterApplicationForm()})
        return render(
            request,
            "transporters/apply.html",
            {"form": TransporterApplicationForm()},
        )

    def post(self, request):
        if hasattr(request.user, "transporter_profile"):
            messages.info(request, "A sua conta já possui uma candidatura de operadora.")
            return redirect("transporter-apply")
        form = TransporterApplicationForm(request.POST)
        if form.is_valid():
            transporter = form.save(commit=False)
            transporter.owner = request.user
            transporter.save()
            if notify_staff_new_transporter(transporter):
                messages.success(request, "Candidatura enviada. O administrador foi notificado por e-mail.")
            else:
                messages.warning(request, "Candidatura enviada, mas o e-mail de notificação falhou. Verifique o SMTP.")
            return redirect("home")
        return render(
            request,
            "transporters/apply.html",
            {"form": form},
        )

class TransporterDashboardView(TransporterRequiredMixin, View):
    def get(self, request):
        return render(
            request,
            "transporters/dashboard.html",
            {"transporter": self.transporter},
        )

class RouteListView(TransporterRequiredMixin, View):
    def get(self, request):
        return render(
            request,
            "transporters/routes.html",
            {
                "form": RouteForm(),
                "routes": self.transporter.routes.all(),
            },
        )

    def post(self, request):
        form = RouteForm(request.POST)
        if form.is_valid():
            route = form.save(commit=False)
            route.transporter = self.transporter
            route.save()
            return redirect("transporter-routes")
        return render(
            request,
            "transporters/routes.html",
            {"form": form, "routes": self.transporter.routes.all()},
        )

class VehicleListView(TransporterRequiredMixin, View):
    def get(self, request):
        return render(
            request,
            "transporters/vehicles.html",
            {
                "form": VehicleForm(),
                "vehicles": self.transporter.vehicles.all(),
            },
        )

    def post(self, request):
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.transporter = self.transporter
            vehicle.save()
            generate_vehicle_seats(vehicle)
            return redirect("transporter-vehicles")
        return render(
            request,
            "transporters/vehicles.html",
            {"form": form, "vehicles": self.transporter.vehicles.all()},
        )

class PaymentAccountListView(TransporterRequiredMixin, View):
    def get(self, request):
        return render(
            request,
            "transporters/payments.html",
            {
                "form": PaymentAccountForm(),
                "accounts": self.transporter.payment_accounts.all(),
            },
        )

    def post(self, request):
        form = PaymentAccountForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.transporter = self.transporter
            account.save()
            return redirect("transporter-payments")
        return render(
            request,
            "transporters/payments.html",
            {
                "form": form,
                "accounts": self.transporter.payment_accounts.all(),
            },
        )
