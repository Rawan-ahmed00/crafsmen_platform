from django.db.models import Q

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Conversation, Message
from .serializers import (
    ConversationSerializer,
    MessageSerializer,
)


class ConversationViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        user = self.request.user

        if not user.is_authenticated:
            return Conversation.objects.none()

        if user.is_staff:
            return Conversation.objects.select_related(
                "customer",
                "technician",
                "offer",
                "offer__service_request",
            ).all()

        return Conversation.objects.filter(
            Q(customer=user) |
            Q(technician=user)
        ).select_related(
            "customer",
            "technician",
            "offer",
            "offer__service_request",
        )


class MessageViewSet(viewsets.ModelViewSet):

    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        user = self.request.user

        if not user.is_authenticated:
            return Message.objects.none()

        if user.is_staff:
            return Message.objects.select_related(
                "conversation",
                "sender",
                "conversation__offer",
            ).all()

        return Message.objects.filter(
            Q(conversation__customer=user) |
            Q(conversation__technician=user)
        ).select_related(
            "conversation",
            "sender",
            "conversation__offer",
        )

    def perform_create(self, serializer):

        conversation = serializer.validated_data["conversation"]

        user = self.request.user

        # التأكد أن المستخدم طرف في المحادثة
        if (
            conversation.customer_id != user.id
            and conversation.technician_id != user.id
            and not user.is_staff
        ):
            raise PermissionDenied(
                "You are not a participant in this conversation."
            )

        # المحادثة يجب أن تكون مرتبطة بعرض
        if conversation.offer_id is None:
            raise PermissionDenied(
                "This conversation is not linked to an offer."
            )

        serializer.save(
            sender=user
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="mark-read",
    )
    def mark_read(self, request, pk=None):

        message = self.get_object()

        # لا يمكن تعليم رسالة كمقروءة إلا لو المستخدم
        # طرف في المحادثة
        conversation = message.conversation

        if (
            conversation.customer_id != request.user.id
            and conversation.technician_id != request.user.id
            and not request.user.is_staff
        ):
            raise PermissionDenied(
                "You are not a participant in this conversation."
            )

        message.is_read = True

        message.save(
            update_fields=["is_read"]
        )

        return Response({
            "message": "Message marked as read."
        })

    def update(self, request, *args, **kwargs):

        return Response(
            {
                "detail": "Messages cannot be updated."
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def partial_update(self, request, *args, **kwargs):

        return Response(
            {
                "detail": "Messages cannot be updated."
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def destroy(self, request, *args, **kwargs):

        return Response(
            {
                "detail": "Messages cannot be deleted."
            },
            status=status.HTTP_405_METHOD)