from django.db import transaction
from django.db.models import Sum, Count
from django.utils import timezone

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import IsAdmin

from .models import Commission
from .serializers import CommissionSerializer


class CommissionViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = CommissionSerializer
    permission_classes = [IsAdmin]

    queryset = Commission.objects.select_related(
        "service_request",
        "service_request__selected_technician",
    ).all()

    @action(
        detail=True,
        methods=["post"],
        url_path="mark-paid",
    )
    @transaction.atomic
    def mark_paid(self, request, pk=None):

        commission = (
            Commission.objects
            .select_for_update()
            .select_related(
                "service_request",
                "service_request__selected_technician",
            )
            .get(pk=pk)
        )

        # منع تسجيل الدفع أكثر من مرة
        if commission.status == Commission.Status.PAID:
            return Response(
                {
                    "detail": "Commission has already been paid."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        commission.status = Commission.Status.PAID
        commission.paid_at = timezone.now()

        commission.save(
            update_fields=[
                "status",
                "paid_at",
            ]
        )

        return Response(
            {
                "message": "Commission marked as paid successfully.",
                "commission_id": commission.id,
                "status": commission.status,
                "paid_at": commission.paid_at,
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="weekly-report",
    )
    def weekly_report(self, request):

        now = timezone.now()

        start_date = now - timezone.timedelta(days=7)

        commissions = Commission.objects.filter(
            created_at__gte=start_date
        )

        report = commissions.aggregate(
            total_commissions=Count("id"),
            total_order_amount=Sum("order_amount"),
            total_commission_amount=Sum("commission_amount"),
        )

        paid = commissions.filter(
            status=Commission.Status.PAID
        ).aggregate(
            count=Count("id"),
            amount=Sum("commission_amount"),
        )

        pending = commissions.filter(
            status=Commission.Status.PENDING
        ).aggregate(
            count=Count("id"),
            amount=Sum("commission_amount"),
        )

        return Response(
            {
                "period": {
                    "from": start_date,
                    "to": now,
                },

                "total_commissions": (
                    report["total_commissions"] or 0
                ),

                "total_order_amount": (
                    report["total_order_amount"] or 0
                ),

                "total_commission_amount": (
                    report["total_commission_amount"] or 0
                ),

                "paid": {
                    "count": paid["count"] or 0,
                    "amount": paid["amount"] or 0,
                },

                "pending": {
                    "count": pending["count"] or 0,
                    "amount": pending["amount"] or 0,
                },
            }
        )