from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class Role(models.TextChoices):

        CUSTOMER = "customer", "Customer"
        TECHNICIAN = "technician", "Technician"
        ADMIN = "admin", "Admin"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER
    )

    phone = models.CharField(
        max_length=20,
        unique=True
    )

    profile_image = models.ImageField(
        upload_to="profiles/",
        null=True,
        blank=True
    )

    is_verified = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.username


class TechnicianProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="technician_profile"
    )

    service_type = models.CharField(
        max_length=100
    )

    national_id = models.ImageField(
        upload_to="identity/"
    )

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0
    )

    completed_orders = models.PositiveIntegerField(
        default=0
    )

    response_time = models.FloatField(
        default=0
    )

    latitude = models.FloatField(
        null=True,
        blank=True
    )

    longitude = models.FloatField(
        null=True,
        blank=True
    )

    is_approved = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return (
            f"{self.user.username} "
            f"- {self.service_type}"
        )