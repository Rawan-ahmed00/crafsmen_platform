from rest_framework import serializers

from .models import User, TechnicianProfile


class AdminUserSerializer(serializers.ModelSerializer):

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
            "is_active",
            "is_staff",
            "date_joined",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "date_joined",
            "created_at",
            "updated_at",
        ]


class AdminTechnicianSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source="user.username",
        read_only=True
    )

    email = serializers.EmailField(
        source="user.email",
        read_only=True
    )

    phone = serializers.CharField(
        source="user.phone",
        read_only=True
    )

    is_active = serializers.BooleanField(
        source="user.is_active",
        read_only=True
    )

    is_verified = serializers.BooleanField(
        source="user.is_verified",
        read_only=True
    )

    profile_image = serializers.ImageField(
        source="user.profile_image",
        read_only=True
    )

    class Meta:
        model = TechnicianProfile

        fields = [
            "id",
            "username",
            "email",
            "phone",
            "service_type",
            "national_id",
            "profile_image",
            "rating",
            "completed_orders",
            "response_time",
            "latitude",
            "longitude",
            "is_approved",
            "is_verified",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "username",
            "email",
            "phone",
            "profile_image",
            "rating",
            "completed_orders",
            "response_time",
            "is_verified",
            "is_active",
            "created_at",
            "updated_at",
        ]