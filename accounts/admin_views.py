from django.db import transaction

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .models import TechnicianProfile, User
from .admin_serializers import (
    AdminTechnicianSerializer,
    AdminUserSerializer,
)


class AdminTechnicianViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = AdminTechnicianSerializer
    permission_classes = [IsAdminUser]

    queryset = TechnicianProfile.objects.select_related(
        "user"
    ).all()

    @action(
        detail=False,
        methods=["get"],
        url_path="pending",
    )
    def pending(self, request):

        technicians = self.get_queryset().filter(
            is_approved=False
        )

        serializer = self.get_serializer(
            technicians,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="approve",
    )
    @transaction.atomic
    def approve(self, request, pk=None):

        technician = self.get_object()
        user = technician.user

        technician.is_approved = True
        technician.save(
            update_fields=[
                "is_approved",
                "updated_at",
            ]
        )

        user.is_verified = True
        user.is_active = True
        user.save(
            update_fields=[
                "is_verified",
                "is_active",
                "updated_at",
            ]
        )

        return Response(
            {
                "message": "Technician approved successfully.",
                "technician_id": technician.id,
                "username": user.username,
                "is_approved": technician.is_approved,
                "is_verified": user.is_verified,
                "is_active": user.is_active,
            },
            status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="suspend",
    )
    @transaction.atomic
    def suspend(self, request, pk=None):

        technician = self.get_object()
        user = technician.user

        user.is_active = False
        user.save(
            update_fields=[
                "is_active",
                "updated_at",
            ]
        )

        return Response(
            {
                "message": "Technician suspended successfully.",
                "technician_id": technician.id,
                "username": user.username,
                "is_active": user.is_active,
            },
            status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="activate",
    )
    @transaction.atomic
    def activate(self, request, pk=None):

        technician = self.get_object()
        user = technician.user

        if not technician.is_approved:
            return Response(
                {
                    "detail":
                    "Technician must be approved before activation."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user.is_active = True
        user.is_verified = True

        user.save(
            update_fields=[
                "is_active",
                "is_verified",
                "updated_at",
            ]
        )

        return Response(
            {
                "message": "Technician activated successfully.",
                "technician_id": technician.id,
                "username": user.username,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
            },
            status=status.HTTP_200_OK
        )


class AdminUserViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUser]

    queryset = User.objects.all().order_by(
        "-created_at"
    )

    @action(
        detail=True,
        methods=["post"],
        url_path="suspend",
    )
    def suspend(self, request, pk=None):

        user = self.get_object()

        if user == request.user:
            return Response(
                {
                    "detail":
                    "You cannot suspend your own admin account."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user.is_active = False

        user.save(
            update_fields=[
                "is_active",
                "updated_at",
            ]
        )

        return Response(
            {
                "message": "User suspended successfully.",
                "user_id": user.id,
                "username": user.username,
                "is_active": user.is_active,
            },
            status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="activate",
    )
    def activate(self, request, pk=None):

        user = self.get_object()

        user.is_active = True

        user.save(
            update_fields=[
                "is_active",
                "updated_at",
            ]
        )

        return Response(
            {
                "message": "User activated successfully.",
                "user_id": user.id,
                "username": user.username,
                "is_active": user.is_active,
            },
            status=status.HTTP_200_OK
        )