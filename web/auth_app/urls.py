from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from . import views
from .views import CityViewSet

app_name = "auth_app"

router = DefaultRouter()
router.register("client", views.ClientAccountViewSet, basename="client")
router.register("provider", views.ProviderAccountViewSet, basename="provider")
router.register("courier", views.CourierAccountViewSet, basename="courier")
router.register("master", views.MasterAccountViewSet, basename="master")
router.register("cities", CityViewSet, basename="cities")

urlpatterns = [
    path("log-in/", views.LogInView.as_view(), name="log-in"),
    path("sms-code/verify/", views.VerifyEmailView.as_view(), name="code-verify"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),

    path("accounts/list/", views.AccountViewSet.as_view({'get': 'accounts_list'}), name="accounts_list"),
]

urlpatterns += router.urls
