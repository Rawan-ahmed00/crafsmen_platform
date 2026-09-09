from rest_framework import serializers
from django.db.transaction import atomic

from .models import User, TechnicianProfile


class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    service_type = serializers.CharField(
        write_only=True,
        required=False
    )

    national_id = serializers.ImageField(
        write_only=True,
        required=False
    )

    latitude = serializers.FloatField(
        write_only=True,
        required=False
    )

    longitude = serializers.FloatField(
        write_only=True,
        required=False
    )

    class Meta:
        model = User

        fields = [
            "username",
            "email",
            "phone",
            "password",
            "role",
            "service_type",
            "national_id",
            "latitude",
            "longitude",
            "profile_image",
        ]

    def validate_role(self, value):

        if value == User.Role.ADMIN:
            raise serializers.ValidationError(
                "You cannot register as admin."
            )

        return value

    def validate_phone(self, value):

        if not value.isdigit():
            raise serializers.ValidationError(
                "Phone must contain numbers only."
            )

        return value

    def validate(self, attrs):

        role = attrs.get("role")

        if role == User.Role.TECHNICIAN:

            if not attrs.get("service_type"):
                raise serializers.ValidationError({
                    "service_type":
                    "Service type is required for technicians."
                })

            if not attrs.get("national_id"):
                raise serializers.ValidationError({
                    "national_id":
                    "National ID image is required for technicians."
                })

        return attrs

    def create(self, validated_data):

        service_type = validated_data.pop(
            "service_type",
            None
        )

        national_id = validated_data.pop(
            "national_id",
            None
        )

        latitude = validated_data.pop(
            "latitude",
            None
        )

        longitude = validated_data.pop(
            "longitude",
            None
        )

        password = validated_data.pop(
            "password"
        )

        user = User.objects.create_user(
            password=password,
            **validated_data
        )

        # Technician registration
        if user.role == User.Role.TECHNICIAN:

            user.is_active = False
            user.is_verified = False

            user.save(
                update_fields=[
                    "is_active",
                    "is_verified",
                    "updated_at",
                ]
            )

            TechnicianProfile.objects.create(
                user=user,
                service_type=service_type,
                national_id=national_id,
                latitude=latitude,
                longitude=longitude,
            )

        return user


class LoginSerializer(serializers.Serializer):

    username = serializers.CharField()

    password = serializers.CharField(
        write_only=True
    )


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User

        fields = [
            "id",
            "username",
            "email",
            "phone",
            "role",
            "profile_image",
            "is_verified",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "role",
            "is_verified",
            "created_at",
        ]


class TechnicianProfileSerializer(
    serializers.ModelSerializer
):

    user = UserSerializer(
        read_only=True
    )

    class Meta:
        model = TechnicianProfile

        fields = [
            "id",
            "user",
            "service_type",
            "national_id",
            "rating",
            "completed_orders",
            "response_time",
            "latitude",
            "longitude",
            "is_approved",
            "created_at",
        ]

        read_only_fields = [
            "rating",
            "completed_orders",
            "response_time",
            "is_approved",
        ]


class NearbyTechnicianSerializer(
    serializers.ModelSerializer
):

    username = serializers.CharField(
        source="user.username"
    )

    rating = serializers.DecimalField(
        max_digits=3,
        decimal_places=2
    )

    class Meta:
        model = TechnicianProfile

        fields = [
            "id",
            "username",
            "service_type",
            "rating",
            "completed_orders",
            "response_time",
            "latitude",
            "longitude",
        ]