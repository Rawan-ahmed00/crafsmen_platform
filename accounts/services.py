from math import radians, sin, cos, sqrt, atan2

from .models import TechnicianProfile


def calculate_distance(
    lat1,
    lon1,
    lat2,
    lon2
):
    """
    Calculate distance between two coordinates
    using Haversine formula.
    """

    if None in [lat1, lon1, lat2, lon2]:
        return None

    earth_radius = 6371

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return earth_radius * c


def get_nearby_technicians(
    latitude,
    longitude,
    service_type,
    max_distance=20
):
    """
    Return approved technicians sorted by:
    1. Distance
    2. Rating
    3. Response time
    """

    technicians = TechnicianProfile.objects.filter(
        service_type__iexact=service_type,
        is_approved=True,
        user__is_verified=True,
        latitude__isnull=False,
        longitude__isnull=False,
    ).select_related("user")

    results = []

    for technician in technicians:

        distance = calculate_distance(
            latitude,
            longitude,
            technician.latitude,
            technician.longitude,
        )

        if distance is None:
            continue

        if distance <= max_distance:

            results.append({
                "technician": technician,
                "distance": round(distance, 2),
            })

    results.sort(
        key=lambda item: (
            item["distance"],
            -float(item["technician"].rating),
            item["technician"].response_time,
        )
    )

    return results