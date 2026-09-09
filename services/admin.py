from django.contrib import admin

from .models import ServiceRequest


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "request_number",
        "customer",
        "service_type",
        "status",
        "selected_technician",
        "final_price",
        "created_at",
    ]

    list_filter = [
        "status",
        "service_type",
    ]

    search_fields = [
        "request_number",
        "customer__username",
        "customer__phone",
        "selected_technician__username",
    ]

    readonly_fields = [
        "request_number",
        "created_at",
        "updated_at",
    ]
