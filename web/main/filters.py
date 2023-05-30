from django_filters import rest_framework as filters

from auth_app.models import Account
from .models import Statement


class NumberInFilter(filters.BaseInFilter, filters.NumberFilter):
    pass


class StatementFilter(filters.FilterSet):
    is_active = filters.BooleanFilter(field_name='is_active')
    is_completed = filters.BooleanFilter(field_name='is_completed')
    is_in_work = filters.BooleanFilter(field_name='is_in_work')
    is_viewed = filters.BooleanFilter(method='is_viewed_filter')
    product_category = NumberInFilter(method='product_category_filter')

    def is_viewed_filter(self, queryset, name, value):
        # todo need to get account_id argument here and filter by viewed responses
        return queryset

    def product_category_filter(self, queryset, name, value: list[int]):
        print("-----value------", value)
        return queryset.filter(product_category_id__in=value)

    class Meta:
        model = Statement
        fields = ["is_active", "is_completed", "is_viewed"]


class AccountFilter(filters.FilterSet):
    type = filters.CharFilter(field_name="type")

    class Meta:
        model = Account
        fields = ["type"]
