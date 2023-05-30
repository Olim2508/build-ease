from django.db.models import QuerySet
from django.utils import timezone


class ConfirmationQuerySet(QuerySet):
    def verify(self, phone, code):
        query = self.order_by('-id')
        query = query.filter(user__phone_number=phone)
        query = query.filter(code=code)
        query = query.filter(expires_at__gte=timezone.now())
        query = query.filter(is_used=False)
        return query.exists()
