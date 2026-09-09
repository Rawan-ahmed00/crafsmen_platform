from rest_framework import serializers

from .models import ServiceRequest


class ServiceRequestSerializer(serializers.ModelSerializer):

    customer_name = serializers.CharField(
        source="customer.username",
        read_only=True
    )

    technician_name = serializers.CharField(
        source="selected_technician.username",
        read_only=True
    )

    class Meta:

        model = ServiceRequest

        fields = [
            "id",
            "request_number",
            "customer",
            "customer_name",
            "service_type",
            "location",
            "latitude",
            "longitude",
            "description",
            "image",
            "status",
            "selected_technician",
            "technician_name",
            "final_price",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "request_number",
            "customer",
            "customer_name",
            "status",
            "selected_technician",
            "technician_name",
            "final_price",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):

        service_request = self.instance

        
        if service_request:

            if service_request.status not in [
                ServiceRequest.Status.PENDING,
                ServiceRequest.Status.OPEN,
            ]:
                raise serializers.ValidationError(
                    "This request cannot be edited anymore."
                )

        
        latitude = attrs.get("latitude")
        longitude = attrs.get("longitude")

        if latitude is not None:
            if not -90 <= latitude <= 90:
                raise serializers.ValidationError({
                    "latitude":
                        "Latitude must be between -90 and 90."
                })

        if longitude is not None:
            if not -180 <= longitude <= 180:
                raise serializers.ValidationError({
                    "longitude":
                        "Longitude must be between -180 and 180."
                })

        return attrs