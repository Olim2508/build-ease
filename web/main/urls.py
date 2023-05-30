from django.urls import path
from rest_framework.routers import DefaultRouter

from main.views import ProductCategoryViewSet, WorkTypeViewSet, VehicleTypeViewSet, ProductStatementViewSet, \
    ResponseViewSet, StatementViewSet, CourierStatementViewSet, MasterStatementViewSet, RatingViewSet, RatingDetailView, \
    FavoriteViewSet, ChatResponseCreateView

app_name = 'main'

router = DefaultRouter()
router.register("statement", StatementViewSet, basename="statement")
router.register("product-statement", ProductStatementViewSet, basename="product-statement")
router.register("master-statement", MasterStatementViewSet, basename="master-statement")
router.register("courier-statement", CourierStatementViewSet, basename="courier-statement")
router.register("response", ResponseViewSet, basename="response")
router.register("rating", RatingViewSet, basename="rating")
router.register("favorites", FavoriteViewSet, basename="favorites")

urlpatterns = [
    path("product-category/list/", ProductCategoryViewSet.as_view({"get": "list"}), name="product-category-list"),
    path("work-type/list/", WorkTypeViewSet.as_view({"get": "list"}), name="work-type-list"),
    path("vehicle-type/list/", VehicleTypeViewSet.as_view({"get": "list"}), name="vehicle-type-list"),
    path("rating/<int:pk>", RatingDetailView.as_view(), name="rating-detail"),
    path("chat-response/", ChatResponseCreateView.as_view(), name="chat-response"),
]


urlpatterns += router.urls
