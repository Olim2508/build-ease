import json
from uuid import UUID

from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from channels.generic.websocket import JsonWebsocketConsumer

from auth_app.models import Account
from chats.api.serializers import MessageSerializer

from chats.models import Conversation, Message

User = get_user_model()


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)


class ChatConsumer(JsonWebsocketConsumer):
    """
    This consumer is used to show user's online status,
    and send notifications.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None
        self.conversation_name = None
        self.conversation = None

    def connect(self):
        self.user = self.scope["user"]
        self.from_user = self.scope["from_user"]
        self.to_user = self.scope["to_user"]
        if not self.user.is_authenticated:
            return

        self.accept()
        self.conversation_name = (
            f"{self.scope['url_route']['kwargs']['conversation_name']}"
        )
        self.conversation, created = Conversation.objects.get_or_create(
            name=self.conversation_name
        )

        async_to_sync(self.channel_layer.group_add)(
            self.conversation_name,
            self.channel_name,
        )

        self.conversation.online.add(self.from_user)

        messages = self.conversation.messages.all().order_by('-timestamp')[0:10]

        message_count = self.conversation.messages.all().count()

        self.send_json(
            {
                "type": "last_50_messages",
                "messages": MessageSerializer(messages, many=True).data,
                "has_more": message_count > 5,
            }
        )

    def disconnect(self, code):
        if self.user.is_authenticated:
            # send the leave event to the room
            async_to_sync(self.channel_layer.group_send)(
                self.conversation_name,
                {
                    "type": "user_leave",
                    "user": self.from_user,
                },
            )
            # self.conversation.online.remove(self.from_user)
        return super().disconnect(code)

    def get_receiver(self):
        from_user = self.from_user
        pks = self.conversation_name.split("__")
        for pk in pks:
            if pk != from_user:
                # This is the receiver
                return Account.objects.get(id=pk)

    def receive_json(self, content, **kwargs):
        message_type = content["type"]

        # if message_type == "read_messages":
        #     messages_to_me = self.conversation.messages.filter(to_user=self.user)
        #     messages_to_me.update(read=True)
        #
        #     # Update the unread message count
        #     unread_count = Message.objects.filter(to_user=self.user, read=False).count()
        #     async_to_sync(self.channel_layer.group_send)(
        #         phone + "__notifications",
        #         {
        #             "type": "unread_count",
        #             "unread_count": unread_count,
        #         },
        #     )
        if message_type == "chat_message":
            message = Message.objects.create(
                from_user_id=self.from_user,
                to_user_id=self.to_user,
                content=content["message"],
                conversation=self.conversation,
            )

            async_to_sync(self.channel_layer.group_send)(
                self.conversation_name,
                {
                    "type": "chat_message_echo",
                    "name": self.from_user,
                    "message": MessageSerializer(message).data,
                },
            )
            notification_group_name = self.from_user + "__notifications"
            async_to_sync(self.channel_layer.group_send)(
                notification_group_name,
                {
                    "type": "new_message_notification",
                    "name": self.from_user,
                    "message": MessageSerializer(message).data,
                },
            )

        return super().receive_json(content, **kwargs)

    def chat_message_echo(self, event):
        self.send_json(event)

    def user_join(self, event):
        self.send_json(event)

    def user_leave(self, event):
        self.send_json(event)

    def typing(self, event):
        self.send_json(event)

    def new_message_notification(self, event):
        self.send_json(event)

    def unread_count(self, event):
        self.send_json(event)

    @classmethod
    def encode_json(cls, content):
        return json.dumps(content, cls=UUIDEncoder)


class NotificationConsumer(JsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None
        self.notification_group_name = None

    def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            return

        self.accept()
        phone = str(self.user.phone_number).replace('+', '')

        # private notification group
        self.notification_group_name = phone + "__notifications"
        self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name,
        )

        # Send count of unread messages
        unread_count = Message.objects.filter(to_user=self.user, read=False).count()
        self.send_json(
            {
                "type": "unread_count",
                "unread_count": unread_count,
            }
        )

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.notification_group_name,
            self.channel_name,
        )
        return super().disconnect(code)

    def new_message_notification(self, event):
        self.send_json(event)

    def unread_count(self, event):
        self.send_json(event)
