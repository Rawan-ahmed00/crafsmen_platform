from django.db import transaction

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import (
    IsCustomer,
    IsTechnicianOrAdmin,
)

from services.services import accept_offer

from notifications.services import create_notification

from chat.models import Conversation

from .models import Offer
from .serializers import OfferSerializer


class OfferViewSet(viewsets.ModelViewSet):

    serializer_class = OfferSerializer



    def get_permissions(self):

        if self.action == "create":
            permission_classes = [IsTechnicianOrAdmin]

        elif self.action in ["accept", "approve"]:
            permission_classes = [IsCustomer]

        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):

        user = self.request.user

        if not user.is_authenticated:
            return Offer.objects.none()

    
        if user.is_staff:
            return Offer.objects.all().select_related(
                "technician",
                "service_request",
            )

        
        if user.role == "customer":
            return Offer.objects.filter(
                service_request__customer=user
            ).select_related(
                "technician",
                "service_request",
            )

        
        if user.role == "technician":
            return Offer.objects.filter(
                technician=user
            ).select_related(
                "service_request",
            )

        return Offer.objects.none()



    @transaction.atomic
    def perform_create(self, serializer):

        service_request = serializer.validated_data["service_request"]

        
        service_request = (
            service_request.__class__
            .objects
            .select_for_update()
            .get(pk=service_request.pk)
        )

        
        if service_request.status not in [
            "pending",
            "open",
            "offer_received",
        ]:
            raise ValidationError({
                "service_request":
                    "This request is no longer accepting offers."
            })

        
        if Offer.objects.filter(
            service_request=service_request,
            technician=self.request.user,
        ).exists():

            raise ValidationError({
                "service_request":
                    "You already submitted an offer for this request."
            })

        
        offers_count = Offer.objects.filter(
            service_request=service_request
        ).count()

        if offers_count >= 5:

            raise ValidationError({
                "service_request":
                    "This request has reached the maximum of 5 offers."
            })

        
        offer = serializer.save(
            technician=self.request.user,
            status=Offer.Status.PENDING,
            is_accepted=False,
        )

        customer = offer.service_request.customer

        
        Conversation.objects.get_or_create(
            offer=offer,
            defaults={
                "customer": customer,
                "technician": offer.technician,
            },
        )

        
        if service_request.status in ["pending", "open"]:
            service_request.status = "offer_received"

            service_request.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

        
        create_notification(
            recipient=customer,
            notification_type="new_offer",
            title="New Offer",
            message=(
                f"{offer.technician.username} "
                f"sent you a new offer."
            ),
        )


    @action(
        detail=True,
        methods=["post"],
        url_path="approve",
    )
    def approve(self, request, pk=None):

        with transaction.atomic():

            
            offer = (
                Offer.objects
                .select_for_update()
                .select_related(
                    "service_request",
                    "technician",
                    "service_request__customer",
                )
                .get(pk=pk)
            )

            service_request = offer.service_request

            
            if service_request.customer_id != request.user.id:
                return Response(
                    {
                        "detail":
                            "You do not have permission to approve this offer."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            
            if offer.status == Offer.Status.ACCEPTED:
                return Response(
                    {
                        "detail":
                            "This offer has already been accepted."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        
            if offer.status == Offer.Status.CANCELLED:
                return Response(
                    {
                        "detail":
                            "This offer has been cancelled."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            
            if service_request.status != "offer_received":
                return Response(
                    {
                        "detail":
                            "This service request is not ready to accept an offer."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        
            Offer.objects.filter(
                service_request=service_request
            ).exclude(
                id=offer.id
            ).update(
                is_accepted=False,
                status=Offer.Status.CANCELLED,
            )

            
            offer.status = Offer.Status.ACCEPTED
            offer.is_accepted = True

            offer.save(
                update_fields=[
                    "status",
                    "is_accepted",
                ]
            )

            
            accept_offer(
                service_request,
                offer,
            )

            
            create_notification(
                recipient=offer.technician,
                notification_type="offer_accepted",
                title="Offer Accepted",
                message=(
                    f"Your offer for "
                    f"{service_request.service_type} "
                    f"has been accepted."
                ),
            )

        return Response(
            {
                "message":
                    "Offer accepted successfully.",
                "offer_id":
                    offer.id,
                "status":
                    offer.status,
                "service_request_status":
                    "accepted",
            },
            status=status.HTTP_200_OK,
        )



    @action(
        detail=True,
        methods=["post"],
        url_path="accept",
    )
    def accept(self, request, pk=None):

        return self.approve(
            request,
            pk,
        )

    

    @action(
        detail=True,
        methods=["post"],
        url_path="cancel",
    )
    def cancel(self, request, pk=None):

        with transaction.atomic():

            offer = (
                Offer.objects
                .select_for_update()
                .select_related(
                    "service_request",
                    "technician",
                )
                .get(pk=pk)
            )

            service_request = offer.service_request
            user = request.user

            
            if offer.status == Offer.Status.ACCEPTED:
                return Response(
                    {
                        "detail":
                            "An accepted offer cannot be cancelled."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        
            if offer.status == Offer.Status.CANCELLED:
                return Response(
                    {
                        "detail":
                            "This offer is already cancelled."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            
            if user.role == "technician":

                if offer.technician_id != user.id:
                    return Response(
                        {
                            "detail":
                                "You can only cancel your own offer."
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )

                recipient = service_request.customer

                notification_type = "offer_accepted"

                notification_title = "Offer Cancelled"

                notification_message = (
                    f"{user.username} cancelled their offer."
                )

            
            elif user.role == "customer":

                if service_request.customer_id != user.id:
                    return Response(
                        {
                            "detail":
                                "You can only cancel offers "
                                "from your own requests."
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )

                recipient = offer.technician

                notification_type = "offer_accepted"

                notification_title = "Offer Cancelled"

                notification_message = (
                    f"The customer cancelled your offer "
                    f"for {service_request.service_type}."
                )

            
            elif user.is_staff:

                recipient = None
                notification_type = None
                notification_title = None
                notification_message = None

            else:
                return Response(
                    {
                        "detail":
                            "You do not have permission to cancel this offer."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            
            offer.status = Offer.Status.CANCELLED
            offer.is_accepted = False

            offer.save(
                update_fields=[
                    "status",
                    "is_accepted",
                ]
            )

        
            if recipient is not None:

                create_notification(
                    recipient=recipient,
                    notification_type=notification_type,
                    title=notification_title,
                    message=notification_message,
                )

        return Response(
            {
                "message":
                    "Offer cancelled successfully.",
                "offer_id":
                    offer.id,
                "status":
                    offer.status,
            },
            status=status.HTTP_200_OK,
        )

    

    def update(self, request, *args, **kwargs):

        return Response(
            {
                "detail":
                    "Offers cannot be updated."
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )



    def partial_update(self, request, *args, **kwargs):

        return Response(
            {
                "detail":
                    "Offers cannot be updated."
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )



    def destroy(self, request, *args, **kwargs):

        return Response(
            {
                "detail":
                    "Offers cannot be deleted."
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )