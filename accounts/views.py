from django.contrib.auth import authenticate

from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from drf_spectacular.utils import extend_schema

from .services import get_nearby_technicians

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    NearbyTechnicianSerializer,
)


@extend_schema(
    request=RegisterSerializer,
    responses={201: UserSerializer},
)
class RegisterView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = RegisterSerializer(
            data=request.data
        )

        if serializer.is_valid():

            user = serializer.save()

            return Response(
                {
                    "message": "Registration successful.",
                    "user": UserSerializer(user).data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LoginView(GenericAPIView):

    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    @extend_schema(
        request=LoginSerializer,
    )
    def post(self, request):

        serializer = self.get_serializer(
            data=request.data
        )

        if not serializer.is_valid():

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        user = authenticate(
            username=username,
            password=password
        )

        if user is None:

            return Response(
                {
                    "detail":
                    "Invalid username or password."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:

            return Response(
                {
                    "detail":
                    "Your account is not active. "
                    "Technicians must be approved by admin first."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Login successful.",

                "user": UserSerializer(user).data,

                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token)
                }
            },
            status=status.HTTP_200_OK
        )


class ProfileView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=UserSerializer
    )
    def get(self, request):

        serializer = UserSerializer(
            request.user
        )

        return Response(
            serializer.data
        )

    @extend_schema(
        request=UserSerializer,
        responses=UserSerializer
    )
    def put(self, request):

        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                serializer.data
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(
    responses=NearbyTechnicianSerializer(many=True)
)
class NearbyTechniciansView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):

        service_type = request.query_params.get(
            "service_type"
        )

        latitude = request.query_params.get(
            "latitude"
        )

        longitude = request.query_params.get(
            "longitude"
        )

        if not all([
            service_type,
            latitude,
            longitude
        ]):

            return Response(
                {
                    "detail":
                    "service_type, latitude and longitude are required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            latitude = float(latitude)
            longitude = float(longitude)

        except (ValueError, TypeError):

            return Response(
                {
                    "detail":
                    "Invalid coordinates."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        technicians = get_nearby_technicians(
            latitude=latitude,
            longitude=longitude,
            service_type=service_type,
        )

        data = []

        for item in technicians:

            technician = NearbyTechnicianSerializer(
                item["technician"]
            ).data

            technician["distance_km"] = item["distance"]

            data.append(technician)

        return Response(data)