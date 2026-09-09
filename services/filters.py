import django_filters

from .models import ServiceRequest


class ServiceRequestFilter(django_filters.FilterSet):

    service_type = django_filters.CharFilter(
        field_name="service_type",
        lookup_expr="iexact"
    )

    status = django_filters.CharFilter(
        field_name="status",
        lookup_expr="iexact"
    )

    request_number = django_filters.UUIDFilter(
        field_name="request_number"
    )

    created_after = django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="gte"
    )

    created_before = django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="lte"
    )

    class Meta:

        model = ServiceRequest

        fields = [
            "service_type",
            "status",
            "request_number",
            "created_after",
            "created_before",
        ]