from decimal import Decimal

from django.db.models import Avg

from .models import Review


def update_technician_rating(technician):

    average_rating = (
        Review.objects
        .filter(technician=technician)
        .aggregate(
            average=Avg("rating")
        )["average"]
    )

    if average_rating is None:
        average_rating = Decimal("0.00")
    else:
        average_rating = Decimal(
            str(round(float(average_rating), 2))
        )

    technician.technician_profile.rating = average_rating

    technician.technician_profile.save(
        update_fields=["rating"]
    )