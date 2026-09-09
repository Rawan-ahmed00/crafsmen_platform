from decimal import Decimal

from django.db import models

from services.models import ServiceRequest


class Commission(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"

    service_request = models.OneToOneField(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name="commission"
    )

    order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("10.00")
    )

    commission_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def calculate_commission(self):
        self.commission_amount = (
            self.order_amount
            * self.commission_rate
            / Decimal("100")
        )

    def save(self, *args, **kwargs):
        self.calculate_commission()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Commission #{self.id}"