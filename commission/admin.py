from django.contrib import admin

from .models import Commission


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "service_request",
        "technician",
        "order_amount",
        "commission_rate",
        "commission_amount",
        "status",
        "created_at",
        "paid_at",
    ]

    list_filter = [
        "status",
        "commission_rate",
        "created_at",
    ]

    search_fields = [
        "service_request__request_number",
        "service_request__customer__username",
        "service_request__selected_technician__username",
    ]

    readonly_fields = [
        "service_request",
        "order_amount",
        "commission_amount",
        "created_at",
        "paid_at",
    ]

    def technician(self, obj):
        technician = obj.service_request.selected_technician

        if technician:
            return technician.username

        return "-"

    technician.short_description = "Technician"