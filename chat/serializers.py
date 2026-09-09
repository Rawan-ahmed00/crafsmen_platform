from rest_framework import serializers

from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):

    sender_username = serializers.CharField(
        source="sender.username",
        read_only=True,
    )

    class Meta:
        model = Message

        fields = [
            "id",
            "conversation",
            "sender",
            "sender_username",
            "message",
            "is_read",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "sender",
            "sender_username",
            "is_read",
            "created_at",
        ]

    def validate_message(self, value):

        if not value.strip():
            raise serializers.ValidationError(
                "Message cannot be empty."
            )

        return value


class ConversationSerializer(serializers.ModelSerializer):

    offer_id = serializers.IntegerField(
        source="offer.id",
        read_only=True,
    )

    service_request_id = serializers.IntegerField(
        source="offer.service_request.id",
        read_only=True,
    )

    customer_username = serializers.CharField(
        source="customer.username",
        read_only=True,
    )

    technician_username = serializers.CharField(
        source="technician.username",
        read_only=True,
    )

    class Meta:
        model = Conversation

        fields = [
            "id",
            "offer",
            "offer_id",
            "service_request_id",
            "customer",
            "customer_username",
            "technician",
            "technician_username",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "offer",
            "offer_id",
            "service_request_id",
            "customer",
            "customer_username",
            "technician",
            "technician_username",
            "created_at",
            "updated_at",
        ]