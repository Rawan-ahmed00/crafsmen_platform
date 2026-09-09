from django.db import transaction

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import ServiceRequest
from .serializers import ServiceRequestSerializer
from .filters import ServiceRequestFilter

from accounts.services import get_nearby_technicians
from accounts.permissions import (
    IsCustomerOrAdmin,
    IsTechnicianOrAdmin,
)

from notifications.services import create_notification
from commission.services import create_commission


class ServiceRequestViewSet(viewsets.ModelViewSet):

    serializer_class = ServiceRequestSerializer
    filterset_class = ServiceRequestFilter

    

    def get_permissions(self):

        if self.action == "create":
            permission_classes = [IsCustomerOrAdmin]

        elif self.action in ["start", "complete"]:
            permission_classes = [IsTechnicianOrAdmin]

        else:
            permission_classes = [IsAuthenticated]

        return [
            permission()
            for permission in permission_classes
        ]

    

    def get_queryset(self):

        user = self.request.user

        
        if not user.is_authenticated:
            return ServiceRequest.objects.none()

        
        if user.is_staff:
            return ServiceRequest.objects.all().select_related(
                "customer",
                "selected_technician",
            )

        
        if user.role == "customer":
            return ServiceRequest.objects.filter(
                customer=user
            ).select_related(
                "customer",
                "selected_technician",
            )

        if user.role == "technician":
            return ServiceRequest.objects.filter(
                selected_technician=user
            ).select_related(
                "customer",
                "selected_technician",
            )

        return ServiceRequest.objects.none()

    

    @transaction.atomic
    def perform_create(self, serializer):

        service_request = serializer.save(
            customer=self.request.user,
            status="pending",
        )


        technicians = get_nearby_technicians(
            latitude=service_request.latitude,
            longitude=service_request.longitude,
            service_type=service_request.service_type,
        )

        
        for item in technicians:

            technician = item["technician"]

            create_notification(
                recipient=technician.user,
                notification_type="new_request",
                title="New Service Request",
                message=(
                    f"New {service_request.service_type} "
                    f"request near you."
                ),
            )



    @action(
        detail=True,
        methods=["post"],
        url_path="start",
    )
    def start(self, request, pk=None):

        with transaction.atomic():

            service_request = (
                ServiceRequest.objects
                .select_for_update()
                .select_related(
                    "customer",
                    "selected_technician",
                )
                .get(pk=pk)
            )

            
            if service_request.selected_technician_id != request.user.id:

                return Response(
                    {
                        "detail":
                            "You are not assigned to this service."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            
            if service_request.status != "accepted":

                return Response(
                    {
                        "detail":
                            "Request must be accepted first."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            
            service_request.status = "in_progress"

            service_request.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

        return Response(
            {
                "message":
                    "Service started successfully.",
                "service_request_id":
                    service_request.id,
                "status":
                    service_request.status,
            },
            status=status.HTTP_200_OK,
        )

    

    @action(
        detail=True,
        methods=["post"],
        url_path="complete",
    )
    def complete(self, request, pk=None):

        with transaction.atomic():

            service_request = (
                ServiceRequest.objects
                .select_for_update()
                .select_related(
                    "customer",
                    "selected_technician",
                )
                .get(pk=pk)
            )

            
            if service_request.selected_technician_id != request.user.id:

                return Response(
                    {
                        "detail":
                            "You are not assigned to this service."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            
            if service_request.status != "in_progress":

                return Response(
                    {
                        "detail":
                            "Service must be in progress."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            
            if not service_request.final_price:

                return Response(
                    {
                        "detail":
                            "Service must have a final price."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            
            service_request.status = "completed"

            service_request.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

            
            create_commission(service_request)

            
            create_notification(
                recipient=service_request.customer,
                notification_type="service_completed",
                title="Service Completed",
                message=(
                    f"Your {service_request.service_type} "
                    f"service has been completed successfully."
                ),
            )

        return Response(
            {
                "message":
                    "Service completed successfully.",
                "service_request_id":
                    service_request.id,
                "status":
                    service_request.status,
                "final_price":
                    service_request.final_price,
            },
            status=status.HTTP_200_OK,
        )