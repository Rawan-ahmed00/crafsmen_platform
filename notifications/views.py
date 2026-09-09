from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        if getattr(self, "swagger_fake_view", False):
            return Notification.objects.none()

        user = self.request.user

        if not user.is_authenticated:
            return Notification.objects.none()

        return Notification.objects.filter(
            recipient=user
        ).order_by("-created_at")

    @action(
        detail=True,
        methods=["post"],
        url_path="mark-read"
    )
    def mark_read(self, request, pk=None):

        notification = self.get_object()

        if notification.is_read:
            return Response({
                "message": "Notification is already marked as read."
            })

        notification.is_read = True
        notification.save(
            update_fields=["is_read"]
        )

        return Response({
            "message": "Notification marked as read."
        })

    @action(
        detail=False,
        methods=["post"],
        url_path="mark-all-read"
    )
    def mark_all_read(self, request):

        updated_count = (
            self.get_queryset()
            .filter(is_read=False)
            .update(is_read=True)
        )

        return Response({
            "message": "All notifications marked as read.",
            "updated_count": updated_count
        })