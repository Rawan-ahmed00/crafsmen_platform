from decimal import Decimal

from django.db import transaction

from .models import Commission


DEFAULT_COMMISSION_RATE = Decimal("10.00")


@transaction.atomic
def create_commission(service_request):



    if service_request.status != "completed":
        raise ValueError(
            "Commission can only be created after service completion."
        )



    if not service_request.selected_technician:
        raise ValueError(
            "Service request must have a selected technician."
        )

    

    if service_request.final_price is None:
        raise ValueError(
            "Service request must have a final price."
        )

    if service_request.final_price <= 0:
        raise ValueError(
            "Final price must be greater than zero."
        )



    commission, created = Commission.objects.get_or_create(
        service_request=service_request,
        defaults={
            "order_amount": service_request.final_price,
            "commission_rate": DEFAULT_COMMISSION_RATE,
            "commission_amount": Decimal("0.00"),
            "status": Commission.Status.PENDING,
        },
    )

    

    if not created:

        
        commission.order_amount = service_request.final_price

        
        commission.calculate_commission()

        commission.save(
            update_fields=[
                "order_amount",
                "commission_amount",
            ]
        )

    return commission 