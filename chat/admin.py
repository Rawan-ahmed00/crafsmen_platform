from django.contrib import admin

from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "offer",
        "customer",
        "technician",
        "created_at",
        "updated_at",
    ]

    search_fields = [
        "customer__username",
        "technician__username",
        "offer__service_request__request_number",
    ]

    list_filter = [
        "created_at",
        "updated_at",
    ]

    readonly_fields = [
        "created_at",
        "updated_at",
    ]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "conversation",
        "sender",
        "message",
        "is_read",
        "created_at",
    ]

    search_fields = [
        "sender__username",
        "message",
    ]

    list_filter = [
        "is_read",
        "created_at",
    ]

    readonly_fields = [
        "created_at",
    ]
