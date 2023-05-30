from dj_rest_auth.jwt_auth import set_jwt_cookies
from django.contrib.auth import get_user_model
from dj_rest_auth import views as auth_views
from rest_framework import viewsets, mixins, status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from django.conf import settings
from django.utils import timezone
from . import serializers
from .choices import AccountChoice
from .models import Account, City

User = get_user_model()


class LogInView(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = serializers.LogInSerializer


class VerifyEmailView(CreateAPIView, auth_views.LoginView):
    serializer_class = serializers.VerifyCodeSerializer

    def post(self, request, *args, **kwargs):
        self.serializer = self.get_serializer(data=request.data)
        self.serializer.is_valid(raise_exception=True)
        self.perform_create(self.serializer)
        self.login()
        account_data = serializers.AccountSerializer(self.user.accounts.all(), many=True).data

        serializer_class = self.get_response_serializer()

        if getattr(settings, 'REST_USE_JWT', False):
            from rest_framework_simplejwt.settings import (
                api_settings as jwt_settings,
            )
            access_token_expiration = (timezone.now() + jwt_settings.ACCESS_TOKEN_LIFETIME)
            refresh_token_expiration = (timezone.now() + jwt_settings.REFRESH_TOKEN_LIFETIME)
            return_expiration_times = getattr(settings, 'JWT_AUTH_RETURN_EXPIRATION', False)

            data = {
                'user': self.user,
                'access_token': self.access_token,
                'refresh_token': self.refresh_token,
            }

            if return_expiration_times:
                data['access_token_expiration'] = access_token_expiration
                data['refresh_token_expiration'] = refresh_token_expiration

            serializer = serializers.UserJWTSerializer(data)
        elif self.token:
            serializer = serializer_class(
                instance=self.token,
                context=self.get_serializer_context(),
            )
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

        response = Response({"user": serializer.data, "accounts": account_data}, status=status.HTTP_200_OK)

        if getattr(settings, 'REST_USE_JWT', False):
            set_jwt_cookies(response, self.access_token, self.refresh_token)

        return response


class ClientAccountViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    serializer_class = serializers.ClientAccountSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Account.objects.filter(type=AccountChoice.CLIENT)
    my_tags = ["Client Account"]


class ProviderAccountViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    permission_classes = (IsAuthenticated,)
    queryset = Account.objects.filter(type=AccountChoice.PROVIDER)
    my_tags = ["Provider Account"]

    def get_serializer_class(self):
        if self.action == 'update':
            return serializers.ProviderAccountUpdateSerializer
        return serializers.ProviderAccountSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CityViewSet(
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = City.objects.all().order_by('title')
    serializer_class = serializers.CitySerializer


class CourierAccountViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    permission_classes = (IsAuthenticated,)
    queryset = Account.objects.filter(type=AccountChoice.COURIER)
    my_tags = ["Courier Account"]

    def get_serializer_class(self):
        if self.action == 'update':
            return serializers.CourierAccountUpdateSerializer
        return serializers.CourierAccountSerializer


class MasterAccountViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    permission_classes = (IsAuthenticated,)
    queryset = Account.objects.filter(type=AccountChoice.MASTER)
    my_tags = ["Master Account"]

    def get_serializer_class(self):
        if self.action == 'update':
            return serializers.MasterAccountUpdateSerializer
        return serializers.MasterAccountSerializer


class AccountViewSet(mixins.ListModelMixin, GenericViewSet):
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "accounts_list":
            return serializers.AccountSerializer

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user).order_by("-id")

    def accounts_list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
