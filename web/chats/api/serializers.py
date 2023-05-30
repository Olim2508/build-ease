from rest_framework import serializers
from django.contrib.auth import get_user_model

from auth_app.models import Account
from auth_app.serializers import AccountSerializer
from chats.models import Message, Conversation
from main.serializers import StatementSerializer, StatementToRepresentationSerializer

User = get_user_model()


class MessageSerializer(serializers.ModelSerializer):
    from_user = serializers.SerializerMethodField()
    to_user = serializers.SerializerMethodField()
    conversation = serializers.SerializerMethodField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['statement'] = StatementToRepresentationSerializer(instance.statement).data
        return data

    class Meta:
        model = Message
        fields = (
            "id",
            "conversation",
            "from_user",
            "to_user",
            "content",
            "timestamp",
            "read",
            "statement",
        )

    def get_conversation(self, obj):
        return str(obj.conversation.id)

    def get_from_user(self, obj):
        return AccountSerializer(obj.from_user).data

    def get_to_user(self, obj):
        return AccountSerializer(obj.to_user).data


class ConversationSerializer(serializers.ModelSerializer):
    other_user = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ("id", "name", "other_user", "last_message")

    def get_last_message(self, obj):
        messages = obj.messages.all().order_by("-timestamp")
        if not messages.exists():
            return None
        message = messages[0]
        return MessageSerializer(message).data

    def get_other_user(self, obj):
        usernames = obj.name.split("__")
        context = {}
        for username in usernames:
            if username != self.context["account"]:
                # This is the other participant
                other_user = Account.objects.get(id=username)
                return AccountSerializer(other_user, context=context).data
