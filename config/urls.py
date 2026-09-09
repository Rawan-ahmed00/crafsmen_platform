from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)


urlpatterns = [


    path(
        "admin/",
        admin.site.urls
    ),


    
    path(
        "api/auth/login/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),

    path(
        "api/auth/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),


    
    path(
        "api/accounts/",
        include("accounts.urls")
    ),



    path(
        "api/services/",
        include("services.urls")
    ),


    
    path(
        "api/offers/",
        include("offers.urls")
    ),


    
    path(
        "api/reviews/",
        include("reviews.urls")
    ),

    path(
        "api/commissions/",
        include("commission.urls")
    ),


    
    path(
        "api/notifications/",
        include("notifications.urls")
    ),

    path(
    "api/chat/",
    include("chat.urls")
    ),


    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),

    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema"
        ),
        name="swagger-ui",
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
