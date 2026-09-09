from django.db import transaction

from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsCustomer

from .models import Review
from .serializers import ReviewSerializer
from .services import update_technician_rating


class ReviewViewSet(viewsets.ModelViewSet):

    serializer_class = ReviewSerializer

    def get_permissions(self):

        if self.action == "create":
            permission_classes = [IsCustomer]
        else:
            permission_classes = [IsAuthenticated]

        return [
            permission()
            for permission in permission_classes
        ]

    def get_queryset(self):

        user = self.request.user

        if not user.is_authenticated:
            return Review.objects.none()

        if user.is_staff:
            return Review.objects.all().select_related(
                "customer",
                "technician",
                "service_request",
            )

        if user.role == "customer":
            return Review.objects.filter(
                customer=user
            ).select_related(
                "technician",
                "service_request",
            )

        if user.role == "technician":
            return Review.objects.filter(
                technician=user
            ).select_related(
                "customer",
                "service_request",
            )

        return Review.objects.none()

    @transaction.atomic
    def perform_create(self, serializer):

        review = serializer.save()

        # تحديث متوسط تقييم الفني
        update_technician_rating(
            review.technician
        )

        # نقل الطلب إلى حالة "تم التقييم"
        service_request = review.service_request

        service_request.status = "reviewed"

        service_request.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

    def update(self, request, *args, **kwargs):

        return Response(
            {
                "detail": "Reviews cannot be updated."
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def partial_update(self, request, *args, **kwargs):

        return Response(
            {
                "detail": "Reviews cannot be updated."
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def destroy(self, request, *args, **kwargs):

        return Response(
            {
                "detail": "Reviews cannot be deleted."
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )