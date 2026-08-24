from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode

from .models import Transporter


def activation_url(request, transporter):
    uid = _uid_for(transporter.owner)
    token = default_token_generator.make_token(transporter.owner)
    path = reverse("transporter-activate", kwargs={"uidb64": uid, "token": token})
    return request.build_absolute_uri(path)


def _uid_for(user):
    from django.utils.http import urlsafe_base64_encode
    from django.utils.encoding import force_bytes
    return urlsafe_base64_encode(force_bytes(user.pk))


def activation_is_valid(transporter, token):
    if not transporter.owner.is_active:
        return False
    if transporter.status != Transporter.Status.ACTIVE or not transporter.activation_required:
        return False
    if not transporter.activation_issued_at:
        return False
    timeout = timedelta(hours=getattr(settings, "PASSAMOZ_ACTIVATION_TIMEOUT_HOURS", 24))
    if timezone.now() > transporter.activation_issued_at + timeout:
        return False
    return default_token_generator.check_token(transporter.owner, token)


def send_transporter_activation(request, transporter):
    recipient = (transporter.email or transporter.owner.email or "").strip()
    if not recipient:
        return False
    url = activation_url(request, transporter)
    hours = getattr(settings, "PASSAMOZ_ACTIVATION_TIMEOUT_HOURS", 24)
    subject = "PassaMoz — ative a sua conta de operadora"
    body = (
        f"Olá, {transporter.owner.get_full_name() or transporter.name}.\n\n"
        f"A sua candidatura da operadora {transporter.name} foi aprovada.\n\n"
        "Para entrar no painel da operadora, primeiro ative a sua conta e defina uma nova senha no link abaixo:\n\n"
        f"{url}\n\n"
        f"Por segurança, este link é válido por {hours} horas e só pode ser usado para uma ativação.\n\n"
        "Depois da ativação, poderá entrar no painel e configurar viaturas, lugares, rotas e viagens.\n\n"
        "Se não solicitou esta conta, ignore este e-mail.\n\n"
        "PassaMoz — Viaje com confiança."
    )
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [recipient], fail_silently=False)
        return True
    except Exception:
        import logging
        logging.getLogger(__name__).exception("Falha ao enviar ativação da operadora")
        return False


def get_user_from_uid(uidb64):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        return get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        return None
