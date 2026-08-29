import json
import logging
from email.message import EmailMessage
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)


class BrevoEmailBackend(BaseEmailBackend):
    """Django email backend using Brevo's HTTPS API (no SMTP ports required)."""

    api_url = "https://api.brevo.com/v3/smtp/email"

    def send_messages(self, email_messages):
        if not email_messages:
            return 0
        sent = 0
        for message in email_messages:
            try:
                if self._send(message):
                    sent += 1
            except Exception:
                if not self.fail_silently:
                    raise
                logger.exception("Falha ao enviar e-mail pela Brevo")
        return sent

    def _send(self, message):
        api_key = getattr(settings, "BREVO_API_KEY", "").strip()
        if not api_key:
            if self.fail_silently:
                return False
            raise RuntimeError("BREVO_API_KEY não está configurada.")

        recipients = []
        for recipient in message.to:
            recipients.append({"email": recipient})
        if not recipients:
            return False

        sender_email = getattr(settings, "BREVO_SENDER_EMAIL", "").strip()
        sender_name = getattr(settings, "BREVO_SENDER_NAME", "PassaMoz").strip()
        if not sender_email:
            # DEFAULT_FROM_EMAIL may be "Name <email@example.com>".
            parsed = EmailMessage()
            parsed["From"] = message.from_email or settings.DEFAULT_FROM_EMAIL
            sender_email = parsed["From"].addresses[0][1]
            sender_name = parsed["From"].addresses[0][0] or sender_name

        text_content = message.body or ""
        html_content = None
        alternatives = getattr(message, "alternatives", []) or []
        for content, mimetype in alternatives:
            if mimetype == "text/html":
                html_content = content
                break

        payload = {
            "sender": {"name": sender_name, "email": sender_email},
            "to": recipients,
            "subject": message.subject,
            "textContent": text_content,
        }
        if html_content:
            payload["htmlContent"] = html_content

        request = Request(
            self.api_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "accept": "application/json",
                "api-key": api_key,
                "content-type": "application/json",
            },
            method="POST",
        )
        timeout = getattr(settings, "EMAIL_TIMEOUT", 20)
        try:
            with urlopen(request, timeout=timeout) as response:
                if 200 <= response.status < 300:
                    return True
                raise RuntimeError(f"Brevo respondeu com HTTP {response.status}")
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            logger.error("Brevo HTTP %s: %s", exc.code, detail)
            if self.fail_silently:
                return False
            raise RuntimeError(f"Brevo HTTP {exc.code}: {detail}") from exc
        except URLError as exc:
            logger.error("Erro de ligação à Brevo: %s", exc)
            if self.fail_silently:
                return False
            raise
