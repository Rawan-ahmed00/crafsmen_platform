from rest_framework import serializers

from .models import Commission


class CommissionSerializer(serializers.ModelSerializer):

    technician = serializers.CharField(
        source="service_request.selected_technician.username",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = Commission

        fields = [
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

        read_only_fields = [
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