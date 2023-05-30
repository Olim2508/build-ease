from django.db.models import Q
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from chats.models import Conversation, Message
from chats.api.paginaters import MessagePagination

from .serializers import MessageSerializer, ConversationSerializer


class ConversationViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = ConversationSerializer
    queryset = Conversation.objects.none()

    def get_queryset(self):
        current_account = self.request.GET.get("current_account")
        queryset = Conversation.objects.filter(
            Q(messages__from_user_id=current_account) | Q(messages__to_user_id=current_account)).distinct()
        return queryset

    def get_serializer_context(self):
        return {"request": self.request, "user": self.request.user, "account": self.request.GET.get("current_account")}


class MessageViewSet(ListModelMixin, GenericViewSet):
    serializer_class = MessageSerializer
    queryset = Message.objects.none()
    pagination_class = MessagePagination

    def get_queryset(self):
        conversation_name = self.request.GET.get("conversation")

        queryset = (
            Message.objects.filter(conversation__name=conversation_name)
            .order_by("-timestamp")
        )
        return queryset
