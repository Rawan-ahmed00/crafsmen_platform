from django.conf import settings
from django.db import models


class Notification(models.Model):

    class NotificationType(models.TextChoices):

        NEW_REQUEST = (
            "new_request",
            "New Request"
        )

        NEW_OFFER = (
            "new_offer",
            "New Offer"
        )

        OFFER_ACCEPTED = (
            "offer_accepted",
            "Offer Accepted"
        )

        SERVICE_COMPLETED = (
            "service_completed",
            "Service Completed"
        )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices
    )

    title = models.CharField(
        max_length=255
    )

    message = models.TextField()

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=[
                    "recipient",
                    "is_read"
                ]
            )
        ]

    def __str__(self):
        return self.title