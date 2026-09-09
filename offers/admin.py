from django.contrib import admin

from .models import Offer


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "service_request",
        "technician",
        "price",
        "estimated_time",
        "is_accepted",
        "created_at",
    ]

    list_filter = [
        "is_accepted",
    ]

    search_fields = [
        "technician__username",
        "service_request__request_number",
    ]
