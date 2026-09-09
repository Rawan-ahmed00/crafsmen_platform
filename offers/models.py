from django.db import models
from django.conf import settings

from services.models import ServiceRequest


class Offer(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        CANCELLED = "cancelled", "Cancelled"

    service_request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name="offers"
    )

    technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="offers"
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    estimated_time = models.PositiveIntegerField()

    message = models.TextField(
        blank=True
    )

    is_accepted = models.BooleanField(
        default=False
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "service_request",
                    "technician"
                ],
                name="unique_technician_offer"
            )
        ]

    def __str__(self):
        return f"Offer {self.id} - {self.status}"