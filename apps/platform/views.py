from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View
from apps.transporters.models import Transporter
from apps.notifications.services import notify_transporter_decision
from apps.transporters.activation import send_transporter_activation

class StaffMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied("Acesso restrito ao administrador.")
        return super().dispatch(request, *args, **kwargs)

class TransporterAdminListView(StaffMixin, View):
    def get(self, request):
        transporters = Transporter.objects.select_related("owner").order_by("-created_at")
        return render(
            request,
            "platform/transporters.html",
            {"transporters": transporters},
        )

class TransporterApproveView(StaffMixin, View):
    def post(self, request, pk):
        transporter = get_object_or_404(Transporter, pk=pk)
        transporter.status = Transporter.Status.ACTIVE
        transporter.approved_at = timezone.now()
        transporter.approved_by = request.user
        transporter.activation_required = True
        transporter.activation_issued_at = timezone.now()
        transporter.save(
            update_fields=["status", "approved_at", "approved_by", "activation_required", "activation_issued_at"]
        )
        decision_ok = notify_transporter_decision(transporter, True, request.user)
        activation_ok = send_transporter_activation(request, transporter)
        if decision_ok and activation_ok:
            messages.success(request, "Operadora aprovada. O e-mail com o link de ativação foi enviado.")
        elif activation_ok:
            messages.warning(request, "Operadora aprovada e link de ativação enviado, mas a notificação interna/e-mail de decisão falhou.")
        else:
            messages.warning(request, "Operadora aprovada, mas o e-mail de ativação falhou. Reenvie o link depois de verificar o SMTP.")
        return redirect("platform-transporters")

class TransporterResendActivationView(StaffMixin, View):
    def post(self, request, pk):
        transporter = get_object_or_404(Transporter, pk=pk)
        if transporter.status != Transporter.Status.ACTIVE:
            messages.error(request, "Apenas operadoras ativas podem receber um link de ativação.")
            return redirect("platform-transporters")
        transporter.activation_required = True
        transporter.activation_issued_at = timezone.now()
        transporter.save(update_fields=["activation_required", "activation_issued_at"])
        if send_transporter_activation(request, transporter):
            messages.success(request, "Novo link de ativação enviado à operadora.")
        else:
            messages.error(request, "Não foi possível enviar o link. Verifique a configuração SMTP.")
        return redirect("platform-transporters")


class TransporterRejectView(StaffMixin, View):
    def post(self, request, pk):
        transporter = get_object_or_404(Transporter, pk=pk)
        transporter.status = Transporter.Status.SUSPENDED
        transporter.save(update_fields=["status"])
        if notify_transporter_decision(transporter, False, request.user):
            messages.success(request, "Candidatura rejeitada e e-mail enviado à operadora.")
        else:
            messages.warning(request, "Candidatura rejeitada, mas o e-mail falhou. Verifique o SMTP.")
        return redirect("platform-transporters")


class TransporterSuspendView(StaffMixin, View):
    def post(self, request, pk):
        transporter = get_object_or_404(Transporter, pk=pk)
        transporter.status = Transporter.Status.SUSPENDED
        transporter.save(update_fields=["status"])
        messages.success(request, "Operadora suspensa.")
        return redirect("platform-transporters")


class SubscriptionListView(StaffMixin, View):
    def get(self, request):
        from .models import MonthlySubscription
        subscriptions = MonthlySubscription.objects.select_related(
            "transporter"
        ).order_by("-reference_month", "transporter__name")
        return render(
            request,
            "platform/subscriptions.html",
            {"subscriptions": subscriptions},
        )

class SubscriptionMarkPaidView(StaffMixin, View):
    def post(self, request, pk):
        from django.utils import timezone
        from django.shortcuts import get_object_or_404
        from .models import MonthlySubscription
        subscription = get_object_or_404(MonthlySubscription, pk=pk)
        subscription.status = MonthlySubscription.Status.PAID
        subscription.paid_at = timezone.now()
        subscription.payment_reference = request.POST.get(
            "payment_reference", ""
        ).strip()
        subscription.save(
            update_fields=[
                "status",
                "paid_at",
                "payment_reference",
            ]
        )
        return redirect("platform-subscriptions")
