from rest_framework import serializers

from .models import Offer


class OfferSerializer(serializers.ModelSerializer):

    class Meta:
        model = Offer

        fields = [
            "id",
            "service_request",
            "technician",
            "price",
            "estimated_time",
            "message",
            "status",
            "is_accepted",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "technician",
            "status",
            "is_accepted",
            "created_at",
        ]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Price must be greater than zero."
            )

        return value

    def validate_estimated_time(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Estimated time must be greater than zero."
            )

        return value

    def validate_service_request(self, service_request):

        if service_request.status not in [
            "pending",
            "open",
            "offer_received",
        ]:
            raise serializers.ValidationError(
                "This service request is not accepting offers."
            )

        return service_request

    def validate(self, attrs):

        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError(
                "Authentication is required."
            )

        technician = request.user
        service_request = attrs.get("service_request")

        if technician.role != "technician":
            raise serializers.ValidationError(
                "Only technicians can create offers."
            )

        if not technician.is_verified:
            raise serializers.ValidationError(
                "Your technician account is not verified."
            )

        if service_request is None:
            raise serializers.ValidationError(
                {
                    "service_request": "Service request is required."
                }
            )

        if Offer.objects.filter(
            service_request=service_request,
            technician=technician,
        ).exists():

            raise serializers.ValidationError(
                "You already submitted an offer for this request."
            )

        if Offer.objects.filter(
            service_request=service_request
        ).count() >= 5:

            raise serializers.ValidationError(
                "This request has reached the maximum of 5 offers."
            )

        return attrs