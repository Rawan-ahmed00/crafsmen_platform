from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    RegisterView,
    LoginView,
    ProfileView,
    NearbyTechniciansView,
)

from .admin_views import (
    AdminTechnicianViewSet,
    AdminUserViewSet,
)


router = DefaultRouter()

router.register(
    "admin/technicians",
    AdminTechnicianViewSet,
    basename="admin-technicians"
)

router.register(
    "admin/users",
    AdminUserViewSet,
    basename="admin-users"
)


urlpatterns = [

    path(
        "register/",
        RegisterView.as_view(),
        name="register"
    ),

    path(
        "login/",
        LoginView.as_view(),
        name="login"
    ),

    path(
        "profile/",
        ProfileView.as_view(),
        name="profile"
    ),

    path(
        "nearby-technicians/",
        NearbyTechniciansView.as_view(),
        name="nearby-technicians"
    ),
]

urlpatterns += router.urls