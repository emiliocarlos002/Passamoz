from django.conf import settings
from django.db import models

class Transporter(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Aguardando aprovação"
        ACTIVE = "active", "Ativa"
        SUSPENDED = "suspended", "Suspensa"

    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="transporter_profile",
    )
    name = models.CharField(max_length=150)
    legal_name = models.CharField(max_length=200, blank=True)
    registration_number = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=30)
    email = models.EmailField()
    address = models.CharField(max_length=255, blank=True)
    province = models.CharField(max_length=80, blank=True)
    city = models.CharField(max_length=100, blank=True)
    main_terminal = models.CharField(max_length=150, blank=True)
    company_type = models.CharField(max_length=50, blank=True)
    founded_year = models.PositiveIntegerField(null=True, blank=True)
    fleet_size = models.PositiveIntegerField(null=True, blank=True)
    responsible_name = models.CharField(max_length=150, blank=True)
    responsible_role = models.CharField(max_length=100, blank=True)
    whatsapp = models.CharField(max_length=30, blank=True)
    website = models.URLField(blank=True)
    vehicle_types = models.CharField(max_length=255, blank=True)
    operating_provinces = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    activation_required = models.BooleanField(default=True)
    activation_issued_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="approved_transporters",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class PaymentAccount(models.Model):
    class Provider(models.TextChoices):
        MPESA = "mpesa", "M-Pesa"
        EMOLA = "emola", "e-Mola"
        MKESH = "mkesh", "mKesh"
        BANK = "bank", "Transferência bancária"

    transporter = models.ForeignKey(
        Transporter,
        on_delete=models.CASCADE,
        related_name="payment_accounts",
    )
    provider = models.CharField(max_length=20, choices=Provider.choices)
    account_name = models.CharField(max_length=150)
    account_number = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    # Manual means the passenger pays to the displayed account and submits the transaction reference.
    # Gateway is reserved for a real provider API integration configured by the platform.
    integration_mode = models.CharField(
        max_length=20,
        choices=(("manual", "Pagamento por referência"), ("gateway", "Gateway/API")),
        default="manual",
    )
    payment_instructions = models.TextField(blank=True, help_text="Instruções mostradas ao passageiro.")
    gateway_wallet_id = models.CharField(max_length=100, blank=True, help_text="Identificador público da carteira no gateway; nunca guardar a chave secreta aqui.")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["transporter", "provider"],
                name="unique_transporter_provider",
            )
        ]

class Route(models.Model):
    transporter = models.ForeignKey(
        Transporter,
        on_delete=models.CASCADE,
        related_name="routes",
    )
    origin = models.CharField(max_length=150)
    destination = models.CharField(max_length=150)
    active = models.BooleanField(default=True)

class Vehicle(models.Model):
    transporter = models.ForeignKey(
        Transporter,
        on_delete=models.CASCADE,
        related_name="vehicles",
    )
    name = models.CharField(max_length=100)
    registration_plate = models.CharField(max_length=30)
    capacity = models.PositiveIntegerField()
    active = models.BooleanField(default=True)

class Seat(models.Model):
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="seats",
    )
    seat_number = models.CharField(max_length=10)
    active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["vehicle", "seat_number"],
                name="unique_vehicle_seat",
            )
        ]
