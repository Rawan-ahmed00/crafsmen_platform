from django.db import transaction

from .models import ServiceRequest


@transaction.atomic
def accept_offer(service_request, offer):

    # قفل الطلب أثناء عملية قبول العرض
    service_request = (
        ServiceRequest.objects
        .select_for_update()
        .get(pk=service_request.pk)
    )

    # التأكد أن العرض تابع لنفس الطلب
    if offer.service_request_id != service_request.id:
        raise ValueError(
            "This offer does not belong to this service request."
        )

    # الطلب لازم يكون مفتوح أو يستقبل عروض
    if service_request.status not in [
        ServiceRequest.Status.OPEN,
        ServiceRequest.Status.OFFER_RECEIVED,
    ]:
        raise ValueError(
            "Request cannot accept an offer."
        )

    # التأكد أن العرض غير مقبول بالفعل
    if offer.is_accepted:
        raise ValueError(
            "This offer has already been accepted."
        )

    # تحديد الفني المختار
    service_request.selected_technician = (
        offer.technician
    )

    # حفظ السعر النهائي
    service_request.final_price = (
        offer.price
    )

    # تغيير حالة الطلب
    service_request.status = (
        ServiceRequest.Status.ACCEPTED
    )

    service_request.save(
        update_fields=[
            "selected_technician",
            "final_price",
            "status",
            "updated_at",
        ]
    )

    return service_request