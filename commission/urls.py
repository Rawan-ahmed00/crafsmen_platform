from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import CommissionViewSet


router = DefaultRouter()


router.register(
    "",
    CommissionViewSet,
    basename="commission"
)


urlpatterns = [
    path("", include(router.urls)),
]
