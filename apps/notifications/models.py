from django.conf import settings
from django.db import models


class Notification(models.Model):
    class Kind(models.TextChoices):
        PAYMENT_CONFIRMED = "payment_confirmed", "Pagamento confirmado"
        PAYMENT_REJECTED = "payment_rejected", "Pagamento rejeitado"
        GENERAL = "general", "Geral"
        OPERATOR_APPLICATION = "operator_application", "Candidatura de operadora"
        OPERATOR_DECISION = "operator_decision", "Decisão sobre operadora"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    kind = models.CharField(max_length=40, choices=Kind.choices, default=Kind.GENERAL)
    title = models.CharField(max_length=160)
    message = models.TextField()
    booking = models.ForeignKey(
        "bookings.Booking",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="notifications",
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("user", "is_read")),
            models.Index(fields=("user", "created_at")),
        ]

    def __str__(self):
        return f"{self.user} - {self.title}"
