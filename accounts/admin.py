from django.contrib import admin

from .models import User, TechnicianProfile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = [
        "username",
        "email",
        "phone",
        "role",
        "is_verified",
        "is_active",
    ]

    list_filter = [
        "role",
        "is_verified",
        "is_active",
    ]

    search_fields = [
        "username",
        "email",
        "phone",
    ]


@admin.register(TechnicianProfile)
class TechnicianProfileAdmin(
    admin.ModelAdmin
):

    list_display = [
        "user",
        "service_type",
        "rating",
        "completed_orders",
        "is_approved",
    ]

    list_filter = [
        "service_type",
        "is_approved",
    ]

    search_fields = [
        "user__username",
        "user__phone",
    ]

    actions = [
        "approve_technicians"
    ]

    @admin.action(
        description="Approve selected technicians"
    )
    def approve_technicians(
        self,
        request,
        queryset
    ):

        queryset.update(
            is_approved=True
        )

        queryset.update(
            user__is_verified=True
        )