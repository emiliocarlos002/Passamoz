import logging
from django.conf import settings
from django.core.mail import send_mail
from .models import Notification
logger = logging.getLogger(__name__)

def _admin_recipients():
    configured = getattr(settings, "PASSAMOZ_ADMIN_EMAIL", "").strip()
    if configured: return [configured]
    from django.contrib.auth import get_user_model
    return list(get_user_model().objects.filter(is_staff=True, is_active=True).exclude(email="").values_list("email", flat=True))

def _send(subject, message, recipients):
    recipients = [r for r in recipients if r]
    if not recipients: return False
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipients, fail_silently=False)
        return True
    except Exception:
        logger.exception("Falha ao enviar e-mail: %s", subject)
        return False

def notify_staff_new_transporter(transporter):
    from django.contrib.auth import get_user_model
    for user in get_user_model().objects.filter(is_staff=True, is_active=True):
        Notification.objects.create(user=user, kind=Notification.Kind.OPERATOR_APPLICATION, title="Nova candidatura de operadora", message=f"A operadora {transporter.name} enviou um pedido de aprovação.")
    return _send(f"PassaMoz — nova candidatura: {transporter.name}", f"Nova candidatura de operadora.\n\nNome: {transporter.name}\nResponsável: {transporter.owner.get_full_name() or transporter.owner.email}\nE-mail: {transporter.email}\nTelefone: {transporter.phone}\n\nEntre no painel administrativo para analisar.", _admin_recipients())

def notify_transporter_decision(transporter, approved, admin_user=None):
    if approved:
        title, subject, body = "Operadora aprovada", "PassaMoz — candidatura aprovada", f"A sua candidatura para {transporter.name} foi APROVADA. Receberá outro e-mail com um link seguro para ativar a conta e definir a sua senha."
    else:
        title, subject, body = "Candidatura rejeitada", "PassaMoz — candidatura rejeitada", f"A sua candidatura para {transporter.name} foi REJEITADA. Entre em contacto com o suporte para obter mais informações."
    Notification.objects.create(user=transporter.owner, kind=Notification.Kind.OPERATOR_DECISION, title=title, message=body)
    return _send(subject, f"Olá, {transporter.owner.get_full_name() or transporter.name}.\n\n{body}", [transporter.owner.email or transporter.email])

def notify_payment_confirmed(booking):
    return Notification.objects.create(user=booking.passenger, kind=Notification.Kind.PAYMENT_CONFIRMED, title="Pagamento confirmado", message="O seu pagamento foi confirmado. O seu bilhete já está disponível com QR Code e PDF.", booking=booking)

def notify_payment_rejected(booking):
    return Notification.objects.create(user=booking.passenger, kind=Notification.Kind.PAYMENT_REJECTED, title="Pagamento rejeitado", message="A operadora não confirmou o pagamento enviado. O lugar reservado foi libertado.", booking=booking)
