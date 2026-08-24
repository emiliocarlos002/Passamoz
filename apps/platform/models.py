from django.db import models
from apps.transporters.models import Transporter


class MonthlySubscription(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendente"
        PAID = "paid", "Paga"
        OVERDUE = "overdue", "Em atraso"
        CANCELLED = "cancelled", "Cancelada"

    transporter = models.ForeignKey(
        Transporter,
        on_delete=models.PROTECT,
        related_name="subscriptions",
    )
    reference_month = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    paid_at = models.DateTimeField(null=True, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["transporter", "reference_month"],
                name="unique_monthly_subscription",
            )
        ]

    def __str__(self):
        return f"{self.transporter.name} - {self.reference_month:%m/%Y}"
