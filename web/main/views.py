from django.db.models import Count, Q, Case, When, Value, BooleanField
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, viewsets, filters, status
from rest_framework.generics import get_object_or_404, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework import generics
from rest_framework.decorators import action
from django_filters import rest_framework as dj_filters

from auth_app.serializers import AccountListSerializer, AccountSerializer
from auth_app.services import AccountService
from main import choices
from main.filters import StatementFilter, AccountFilter
from main.models import ProductCategory, WorkType, VehicleType, Statement, Response as ResponseModel, Rating
from main.paginators import BasePagination
from main.serializers import ProductCategorySerializer, WorkTypeSerializer, VehicleTypeSerializer, \
    ProductStatementSerializer, ProductStatementUpdateSerializer, ResponseSerializer, StatementSerializer, \
    StatementAcceptResponseSerializer, MyStatementSerializer, CourierStatementSerializer, NewStatementsSerializer, \
    MasterStatementSerializer, MasterStatementUpdateSerializer, RatingSerializer, \
    FavoritesSerializer, FavoritesDeleteSerializer, AcceptProductStatementExecutor, ChatResponseSerializer, \
    StatementToRepresentationSerializer, RatingListSerializer, ResponseListSerializer
from main.services import FavoriteService, ResponseService, RatingService


class ProductCategoryViewSet(
    mixins.ListModelMixin,
    GenericViewSet,
):
    permission_classes = (IsAuthenticated,)
    queryset = ProductCategory.objects.all().order_by("-id")
    serializer_class = ProductCategorySerializer


class WorkTypeViewSet(
    mixins.ListModelMixin,
    GenericViewSet,
):
    permission_classes = (IsAuthenticated,)
    queryset = WorkType.objects.all().order_by("-id")
    serializer_class = WorkTypeSerializer


class VehicleTypeViewSet(
    mixins.ListModelMixin,
    GenericViewSet,
):
    permission_classes = (IsAuthenticated,)
    queryset = VehicleType.objects.all().order_by("-id")
    serializer_class = VehicleTypeSerializer


class StatementViewSet(GenericViewSet):
    permission_classes = (IsAuthenticated,)
    my_tags = ["Statement"]
    filterset_class = StatementFilter
    serializer_class = StatementToRepresentationSerializer
    queryset = Statement.objects.order_by("-created_at")
    pagination_class = BasePagination
    filter_backends = [filters.OrderingFilter, dj_filters.DjangoFilterBackend]
    ordering_fields = ['created_at']

    @action(detail=False, methods=['GET'], url_path=r'my-statements',
            serializer_class=MyStatementSerializer, url_name="my_statements_list")
    def my_statements_list(self, request):
        queryset = self.filter_queryset(Statement.objects.filter(account=request.account))
        responses_count_all = Count('response')
        responses_count_not_viewed = Count('response', filter=Q(response__is_viewed=False))
        queryset = queryset \
            .annotate(responses_count_all=responses_count_all) \
            .annotate(responses_count_not_viewed=responses_count_not_viewed)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(methods=['POST'], request_body=StatementAcceptResponseSerializer,
                         operation_description="Не принимаю откликов")
    @action(detail=False, methods=['POST'], url_path=r'accept-responses/(?P<statement_id>\d+)')
    def accept_responses(self, request, statement_id, *args, **kwargs):
        instance = get_object_or_404(Statement, id=statement_id)
        serializer = StatementAcceptResponseSerializer(data=request.data, context={"instance": instance})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(methods=['GET'], operation_description="Для получения списка новых заявок других аккаунтов")
    @action(detail=False, methods=['GET'], url_path=r'new-statements-list', url_name="new_statements_list",
            filterset_class=StatementFilter)
    def new_statements_list(self, request, *args, **kwargs):
        statement_id_list = ResponseService.get_statement_ids_of_account_response(request.account)
        queryset = self.filter_queryset(self.get_queryset().exclude(
            Q(account=request.account) | Q(id__in=statement_id_list))
        )

        # queryset = queryset.annotate(is_response_added=Case(When(image_count=0, then=Value(False)),
        #                                                     default=Value(True), output_field=BooleanField()))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'], url_path=r'statements-with-my-response/(?P<account_id>\d+)')
    def statements_with_my_response(self, request, account_id):
        account_responses_id_list = ResponseModel.objects.filter(account_id=account_id).values_list("id", flat=True)
        queryset = self.filter_queryset(Statement.objects.filter(response__in=account_responses_id_list))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(methods=['POST'], request_body=AcceptProductStatementExecutor,
                         operation_description="Выбрать поставщика")
    @action(detail=False, methods=['POST'], url_path=r'product-statement-accept-executor',
            url_name='product_statement_accept_executor')
    def accept_executor_of_product_statement(self, request, *args, **kwargs):
        serializer = AcceptProductStatementExecutor(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "accepted as executor"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'accepted-statements-list', url_name="accepted_statements_list")
    def accepted_statements_list(self, request, *args, **kwargs):
        """For executor account"""
        queryset = self.get_queryset().filter(executor=request.account)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductStatementSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ProductStatementSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductStatementViewSet(mixins.CreateModelMixin,
                              mixins.DestroyModelMixin,
                              mixins.RetrieveModelMixin,
                              # mixins.ListModelMixin,
                              mixins.UpdateModelMixin,
                              GenericViewSet):
    # permission_classes = (IsAuthenticated,)
    queryset = Statement.objects.order_by("-created_at")
    my_tags = ["Product Statement"]

    def get_serializer_class(self):
        if self.action == 'update':
            return ProductStatementUpdateSerializer
        return ProductStatementSerializer


class MasterStatementViewSet(mixins.CreateModelMixin,
                             mixins.DestroyModelMixin,
                             mixins.RetrieveModelMixin,
                             mixins.UpdateModelMixin,
                             GenericViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Statement.objects.order_by("-created_at")
    my_tags = ["Master Statement"]

    def get_serializer_class(self):
        if self.action == 'update':
            return MasterStatementUpdateSerializer
        return MasterStatementSerializer


class CourierStatementViewSet(mixins.CreateModelMixin,
                              mixins.DestroyModelMixin,
                              mixins.RetrieveModelMixin,
                              # mixins.ListModelMixin,
                              mixins.UpdateModelMixin,
                              GenericViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Statement.objects.all()
    my_tags = ["Courier Statement"]

    def get_serializer_class(self):
        return CourierStatementSerializer


class RatingViewSet(GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = RatingSerializer
    pagination_class = BasePagination
    filter_backends = [dj_filters.DjangoFilterBackend]
    my_tags = ["Ratings (Отзывы)"]

    @swagger_auto_schema(methods=['POST'], request_body=RatingSerializer,
                         operation_description="Добавить отзыв в аккаунт")
    @action(detail=False, methods=['POST'], url_path=r'create', url_name="create")
    def create_rating(self, request, *args, **kwargs):
        serializer = RatingSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        RatingService.create_rating(request.account, serializer.validated_data)
        return Response({"body": "Rating created"}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(methods=['GET'], operation_description="Список отзывов аккаунта")
    @action(detail=False, methods=['GET'], url_path=r'list/(?P<account_id>\d+)', url_name="list",
            serializer_class=RatingListSerializer)
    def get_list_of_ratings(self, request, account_id, *args, **kwargs):
        ratings = Rating.objects.filter(worker_id=account_id).order_by('-created_at')
        queryset = self.filter_queryset(ratings)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RatingDetailView(mixins.UpdateModelMixin, generics.DestroyAPIView, generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = RatingSerializer
    queryset = Rating.objects.all()

    def put(self, request, *args, **kwargs):
        """
        # *Request data for updating*
            {
                "title": "NEW TEMPLATE NAME",
            }
        """
        return self.update(request, *args, **kwargs)


class ResponseViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      GenericViewSet):
    """отклик"""
    # permission_classes = (IsAuthenticated,)
    serializer_class = ResponseSerializer
    queryset = ResponseModel.objects.all()
    pagination_class = BasePagination
    filter_backends = [filters.OrderingFilter, dj_filters.DjangoFilterBackend]
    my_tags = ["Response (отклики)"]
    ordering_fields = ['price']

    @action(detail=False, methods=['GET'], url_path=r'responses-list/(?P<statement_id>\d+)',
            serializer_class=ResponseListSerializer)
    def responses_list(self, request, statement_id):
        queryset = self.filter_queryset(self.queryset.filter(statement_id=statement_id))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ChatResponseCreateView(APIView):
    def post(self, request):
        serializer = ChatResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, 201)


class FavoriteViewSet(GenericViewSet):
    serializer_class = None
    permission_classes = (IsAuthenticated,)
    pagination_class = BasePagination
    filter_backends = [dj_filters.DjangoFilterBackend]
    filterset_class = AccountFilter
    my_tags = ["Favorites (Избранное)"]

    @swagger_auto_schema(methods=['POST'], request_body=FavoritesSerializer,
                         operation_description="Добавить аккаунт в избранное")
    @action(detail=False, methods=['POST'], url_path=r'add', url_name="add_account_to_favorites")
    def add_account_to_favorites(self, request, *args, **kwargs):
        serializer = FavoritesSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        adding_account = AccountService.get_account_by_id(serializer.validated_data['account_id'])
        FavoriteService.add_account_to_favorite(request.account, adding_account)
        return Response({"account_id": ["Account added to favorites successfully"]}, status=status.HTTP_200_OK)

    @swagger_auto_schema(methods=['POST'], request_body=FavoritesDeleteSerializer,
                         operation_description="Удалить аккаунт из избранные")
    @action(detail=False, methods=['POST'], url_path=r'delete', url_name="delete_account_from_favorites")
    def delete_account_from_favorites(self, request, *args, **kwargs):
        serializer = FavoritesDeleteSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        adding_account = AccountService.get_account_by_id(serializer.validated_data['account_id'])
        FavoriteService.delete_account_from_favorite(request.account, adding_account)
        return Response({"account_id": ["Account deleted from favorites successfully"]}, status=status.HTTP_200_OK)

    @swagger_auto_schema(methods=['GET'], operation_description="Список избранных аккаунтов")
    @action(detail=False, methods=['GET'], url_path=r'get-list', url_name="get_list",
            serializer_class=AccountSerializer)
    def get_list_of_favorite_accounts(self, request, *args, **kwargs):
        favorite_accounts_qs = FavoriteService.get_favorite_accounts_of_user(request.account)
        queryset = self.filter_queryset(favorite_accounts_qs)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
