from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "service_request",
        "customer",
        "technician",
        "rating",
        "created_at",
    ]

    list_filter = [
        "rating",
        "created_at",
    ]

    search_fields = [
        "customer__username",
        "technician__username",
        "service_request__request_number",
    ]

    readonly_fields = [
        "customer",
        "technician",
        "service_request",
        "rating",
        "comment",
        "created_at",
    ]