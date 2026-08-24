from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import SetPasswordForm
from django.shortcuts import redirect, render
from django.views import View

from .activation import activation_is_valid, get_user_from_uid
from .models import Transporter


class TransporterActivationView(View):
    template_name = "transporters/activate.html"

    def get(self, request, uidb64, token):
        user = get_user_from_uid(uidb64)
        if not user:
            return render(request, self.template_name, {"invalid": True})
        try:
            transporter = user.transporter_profile
        except Transporter.DoesNotExist:
            return render(request, self.template_name, {"invalid": True})
        if not activation_is_valid(transporter, token):
            return render(request, self.template_name, {"invalid": True, "expired": transporter.status == Transporter.Status.ACTIVE})
        return render(request, self.template_name, {"form": SetPasswordForm(user), "transporter": transporter})

    def post(self, request, uidb64, token):
        user = get_user_from_uid(uidb64)
        if not user:
            return render(request, self.template_name, {"invalid": True})
        try:
            transporter = user.transporter_profile
        except Transporter.DoesNotExist:
            return render(request, self.template_name, {"invalid": True})
        if not activation_is_valid(transporter, token):
            return render(request, self.template_name, {"invalid": True, "expired": True})
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            transporter.activation_required = False
            transporter.save(update_fields=["activation_required"])
            login(request, user)
            messages.success(request, "Conta ativada com sucesso. Bem-vindo ao painel da sua operadora.")
            return redirect("transporter-dashboard")
        return render(request, self.template_name, {"form": form, "transporter": transporter})
