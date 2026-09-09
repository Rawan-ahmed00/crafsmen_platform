import uuid

from django.conf import settings
from django.db import models


class ServiceRequest(models.Model):

    class Status(models.TextChoices):

        PENDING = "pending", "Pending"

        OPEN = "open", "Open"

        OFFER_RECEIVED = (
            "offer_received",
            "Offer Received"
        )

        ACCEPTED = "accepted", "Accepted"

        IN_PROGRESS = (
            "in_progress",
            "In Progress"
        )

        COMPLETED = "completed", "Completed"

        REVIEWED = "reviewed", "Reviewed"

        CANCELLED = "cancelled", "Cancelled"

    request_number = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="service_requests"
    )

    service_type = models.CharField(
        max_length=100
    )

    location = models.CharField(
        max_length=255
    )

    latitude = models.FloatField(
        null=True,
        blank=True
    )

    longitude = models.FloatField(
        null=True,
        blank=True
    )

    description = models.TextField()

    image = models.ImageField(
        upload_to="service_requests/",
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING
    )

    selected_technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_requests"
    )

    final_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["status"]
            ),
            models.Index(
                fields=["service_type"]
            ),
            models.Index(
                fields=["created_at"]
            ),
        ]

    def __str__(self):
        return str(self.request_number)