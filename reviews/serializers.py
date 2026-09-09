from rest_framework import serializers

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review

        fields = [
            "id",
            "customer",
            "technician",
            "service_request",
            "rating",
            "comment",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "customer",
            "technician",
            "created_at",
        ]

    def validate_rating(self, value):

        if not 1 <= value <= 5:
            raise serializers.ValidationError(
                "Rating must be between 1 and 5."
            )

        return value

    def validate(self, attrs):

        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError(
                "Authentication is required."
            )

        service_request = attrs.get("service_request")

        if service_request is None:
            raise serializers.ValidationError(
                {
                    "service_request":
                    "Service request is required."
                }
            )

        # التقييم يكون من العميل صاحب الطلب فقط
        if service_request.customer_id != request.user.id:
            raise serializers.ValidationError(
                "Only the customer can review this service."
            )

        # لازم الخدمة تكون مكتملة
        if service_request.status != "completed":
            raise serializers.ValidationError(
                "Service must be completed first."
            )

        # لازم يكون فيه فني مختار
        if service_request.selected_technician_id is None:
            raise serializers.ValidationError(
                "This service has no selected technician."
            )

        # منع تقييم نفس الطلب أكثر من مرة
        if Review.objects.filter(
            service_request=service_request
        ).exists():
            raise serializers.ValidationError(
                "This service was already reviewed."
            )

        return attrs

    def create(self, validated_data):

        service_request = validated_data["service_request"]

        validated_data["customer"] = (
            self.context["request"].user
        )

        validated_data["technician"] = (
            service_request.selected_technician
        )

        return super().create(validated_data)